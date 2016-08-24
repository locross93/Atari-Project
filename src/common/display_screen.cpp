/* *****************************************************************************
 * A.L.E (Arcade Learning Environment)
 * Copyright (c) 2009-2013 by Yavar Naddaf, Joel Veness, Marc G. Bellemare, 
 *   Matthew Hausknecht, and the Reinforcement Learning and Artificial Intelligence 
 *   Laboratory
 * Released under the GNU General Public License; see License.txt for details. 
 *
 * Based on: Stella  --  "An Atari 2600 VCS Emulator"
 * Copyright (c) 1995-2007 by Bradford W. Mott and the Stella team
 *
 * *****************************************************************************
 *  diplay_screen.cpp 
 *
 *  Supports displaying the screen via SDL. 
 **************************************************************************** */
#include "display_screen.h"
#include "SoundSDL.hxx"
using namespace std;
#ifdef __USE_SDL
DisplayScreen::DisplayScreen(MediaSource* mediaSource,
                             Sound* sound,
                             ColourPalette &palette):
        manual_control_active(true),
        media_source(mediaSource),
        my_sound(sound),
        colour_palette(palette),
        delay_msec(17)
{
    screen_height = media_source->height();
    screen_width = media_source->width();
    assert(window_height >= screen_height);
    assert(window_width >= screen_width);
    yratio = window_height / (float) screen_height;
    xratio = window_width / (float) screen_width;
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_JOYSTICK) < 0) {
        fprintf(stderr, "Could not initialize SDL: %s\n", SDL_GetError());
        exit(1);
    }
    screen = SDL_SetVideoMode(window_width, window_height, 8, SDL_HWPALETTE);
    if (screen == NULL) {
        fprintf(stderr, "Couldn't Initialize Screen: %s\n", SDL_GetError());
        exit(1);
    }
    SDL_WM_SetCaption("ALE Viz", NULL);
    fprintf(stderr, "Screen Display Active. [Manual Control Mode] 'm' "
            "[Slowdown] 'a' [Speedup] 's' [VolumeDown] '[' [VolumeUp] ']'.\n");

    last_frame_time = SDL_GetTicks();

    // SDL_JoystickEventState(SDL_ENABLE);
    // // Check for joystick
    // if(SDL_NumJoysticks()>0){
    //   // Open joystick
    //   joy=SDL_JoystickOpen(0);
      
    //   if(joy)
    //   {
    //     printf("Opened Joystick 0\n");
    //     printf("Name: %s\n", SDL_JoystickName(0));
    //     printf("Number of Axes: %d\n", SDL_JoystickNumAxes(joy));
    //     printf("Number of Buttons: %d\n", SDL_JoystickNumButtons(joy));
    //     printf("Number of Balls: %d\n", SDL_JoystickNumBalls(joy));
    //   }
    //   else
    //     printf("Couldn't open Joystick 0\n");
      
      
    // }else{
    //     printf("No Joystick 0\n");
    // }

}

DisplayScreen::~DisplayScreen() {
    // // Close if opened
    //   if(SDL_JoystickOpened(0))
    //     SDL_JoystickClose(joy);

    SDL_Quit();
}

void DisplayScreen::display_screen() {
    if (SDL_MUSTLOCK(screen)) {
      if (SDL_LockSurface(screen) < 0 ) {
        fprintf(stderr, "Can't lock screen: %s\n", SDL_GetError());
        return;
      }
    }
    // Convert the media sources frame into the screen matrix representation
    int xciel = int(xratio) + 1;
    int yciel = int(yratio) + 1;
    uInt8* pi_curr_frame_buffer = media_source->currentFrameBuffer();
    int y, x, r, g, b;
    SDL_Rect rect;
    for (int i = 0; i < screen_width * screen_height; i++) {
        y = i / screen_width;
        x = i - (y * screen_width);
        colour_palette.getRGB(pi_curr_frame_buffer[i], r, g, b);
        rect.x = (int)(x * xratio);
        rect.y = (int)(y * yratio);
        rect.w = xciel;
        rect.h = yciel;
        SDL_FillRect(screen, &rect, SDL_MapRGB(screen->format, r, g, b));
    }
    if (SDL_MUSTLOCK(screen)) {
      SDL_UnlockSurface(screen);
    }
    SDL_UpdateRect(screen, 0, 0, 0, 0);
    poll();

    // Wait a while, calibrating so that the delay remains the same
    Uint32 newTime = SDL_GetTicks();
    Uint32 delta = newTime - min(last_frame_time, newTime);

    if (delta < delay_msec) {
        SDL_Delay(delay_msec - delta);
    } else {
        // Try to keep up with the delay
        last_frame_time = SDL_GetTicks() + delta - delay_msec;
    }
}

void DisplayScreen::poll() {
    SDL_Event event;
    while(SDL_PollEvent(&event)) {
        handleSDLEvent(event);
    }
};

void DisplayScreen::handleSDLEvent(const SDL_Event& event) {
    
    switch (event.type) {
        case SDL_QUIT:
            exit(0);
            break;
        case SDL_JOYAXISMOTION:
            // std::cout << "joy!\n";
            break;
        case SDL_KEYDOWN:
            switch(event.key.keysym.sym) {
                case SDLK_m:
                    manual_control_active = !manual_control_active;
                    if (manual_control_active) {
                        fprintf(stderr, "Manual Control Enabled: [Move] "
                                "Arrow keys [Fire] Space [NO-OP] Return.\n");
                    } else {
                        fprintf(stderr, "Manual Control Disabled\n");
                    }
                    break;
                case SDLK_s:
                    delay_msec = delay_msec > 5 ? delay_msec - 5 : 0;
                    fprintf(stderr, "[Speedup] %d msec delay\n", delay_msec);
                    break;
                case SDLK_a:
                    delay_msec = delay_msec + 5;
                    fprintf(stderr, "[Slowdown] %d msec delay\n", delay_msec);
                    break;
#ifdef SOUND_SUPPORT
                case SDLK_LEFTBRACKET:
                    fprintf(stderr, "[VolumeDown]\n");
                    for (int i=0; i<5; ++i) {
                        ((SoundSDL*)my_sound)->adjustVolume(-1);
                    }
                    break;
                case SDLK_RIGHTBRACKET:
                    fprintf(stderr, "[VolumeUp]\n");
                    for (int i=0; i<5; ++i) {
                        ((SoundSDL*)my_sound)->adjustVolume(1);
                    }
                    break;
#endif
                default:
                    break;
            }
            break;
        default:
            break;
    }
};

Action DisplayScreen::getUserAction() {
    if (!manual_control_active) {
        return UNDEFINED;
    }

    Action a = PLAYER_A_NOOP;
    // Uint32 buttonmap;
    poll();
    SDL_PumpEvents();
    Uint8* keymap = SDL_GetKeyState(NULL);

    int mdltx, mdlty;
    auto r = SDL_GetRelativeMouseState(&mdltx, &mdlty);

    std::cout << mdltx << " x \n";

    if( !!(r&SDL_BUTTON(SDL_BUTTON_RIGHT)) ){
        std::cout << "Is right\n";
    }

    if( !!(r&SDL_BUTTON(SDL_BUTTON_LEFT)) ){
        std::cout << "Is left\n";
    }


    // std::cout << !!(r&SDL_BUTTON(SDL_BUTTON_RIGHT)) << " is right \n";
    // std::cout << !!(r&SDL_BUTTON(SDL_BUTTON_LEFT)) << " is left \n";


    // std::cout << "is left? " << r&SDL_BUTTON(SDL_BUTTON_LEFT) << "\n";


    // r&SDL_BUTTON(1);
    // std::cout << r << "\n";

    // std::cout << "is left? " << buttonmap[SDL_BUTTON_LEFT] << "\n";
    // std::cout << "is right? " << buttonmap[SDL_BUTTON_RIGHT] << "\n";

    // std::cout << mdltx << ":x:\n";
    // std::cout << mdlty << ":y:\n";


    // Sint16 x_move, y_move;
    // x_move=SDL_JoystickGetAxis(joy, 0);
    // y_move=SDL_JoystickGetAxis(joy, 1);
    // Uint8 joyButton;
    
    
    // Break out of this loop if the 'p' key is pressed
    if (keymap[SDLK_p]) {
      return PLAYER_A_NOOP;
      // Triple Actions
    } else if (keymap[SDLK_UP] && keymap[SDLK_RIGHT] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_UPRIGHTFIRE;
    } else if (keymap[SDLK_UP] && keymap[SDLK_LEFT] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_UPLEFTFIRE;
    } else if (keymap[SDLK_DOWN] && keymap[SDLK_RIGHT] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_DOWNRIGHTFIRE;
    } else if (keymap[SDLK_DOWN] && keymap[SDLK_LEFT] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_DOWNLEFTFIRE;
      // Double Actions
    } else if (keymap[SDLK_UP] && keymap[SDLK_LEFT]) {
      a = PLAYER_A_UPLEFT;
    } else if (keymap[SDLK_UP] && keymap[SDLK_RIGHT]) {
      a = PLAYER_A_UPRIGHT;
    } else if (keymap[SDLK_DOWN] && keymap[SDLK_LEFT]) {
      a = PLAYER_A_DOWNLEFT;
    } else if (keymap[SDLK_DOWN] && keymap[SDLK_RIGHT]) {
      a = PLAYER_A_DOWNRIGHT;
    } else if (keymap[SDLK_UP] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_UPFIRE;
    } else if (keymap[SDLK_DOWN] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_DOWNFIRE;
    } else if (keymap[SDLK_LEFT] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_LEFTFIRE;
    } else if (keymap[SDLK_RIGHT] && keymap[SDLK_SPACE]) {
      a = PLAYER_A_RIGHTFIRE;
      // Single Actions
    } else if (keymap[SDLK_SPACE] || keymap[SDLK_2] || keymap[SDLK_3] || !!(r&SDL_BUTTON(SDL_BUTTON_RIGHT)) || !!(r&SDL_BUTTON(SDL_BUTTON_LEFT))) {
      a = PLAYER_A_FIRE;
    } else if (keymap[SDLK_RETURN]) {
      a = PLAYER_A_NOOP;
    } else if (keymap[SDLK_LEFT] || mdltx < 0) {
      a = PLAYER_A_LEFT;
    } else if (keymap[SDLK_RIGHT] || mdltx > 0) {
      a = PLAYER_A_RIGHT;
    } else if (keymap[SDLK_UP] || mdlty < 0) {
      a = PLAYER_A_UP;
    } else if (keymap[SDLK_DOWN] || mdlty > 0) {
      a = PLAYER_A_DOWN;
    }else if (keymap[SDLK_5]){
        a = MRI_PULSE;
    }


    return a;
}

#endif // __USE_SDL
