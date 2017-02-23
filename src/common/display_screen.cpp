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
 //ive added this
#include <iostream>
#include "display_screen.h"
#include "SoundSDL.hxx"
#include <chrono>
#include <thread>
#include <unistd.h>
using namespace std;
#ifdef __USE_SDL
DisplayScreen::DisplayScreen(MediaSource* mediaSource,
                             Sound* sound,
                             ColourPalette &palette):
        manual_control_active(true),
        block_on(true),
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

    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        fprintf(stderr, "Could not initialize SDL: %s\n", SDL_GetError());
        exit(1);
    }
    screen = SDL_SetVideoMode(window_width, window_height, 8, SDL_HWPALETTE);
    // uncomment below for full screen 
    // screen = SDL_SetVideoMode(window_width, window_height, 8, SDL_HWPALETTE | SDL_FULLSCREEN);
    // SDL_ShowCursor(0);
    // SDL_SetRelativeMouseMode(SDL_TRUE);
    // trap mouse cursor in video frame
    // SDL_WM_GrabInput( SDL_GRAB_ON );

    if (screen == NULL) {
        fprintf(stderr, "Couldn't Initialize Screen: %s\n", SDL_GetError());
        exit(1);
    }
    SDL_WM_SetCaption("ALE Viz", NULL);
    //Uint32 FullscreenFlag = SDL_WINDOW_FULLSCREEN;
    //SDL_SetWindowFullscreen(screen, 1, SDL_GRAB_FULLSCREEN);
    fprintf(stderr, "Screen Display Active. [Manual Control Mode] 'm' "
            "[Slowdown] 'a' [Speedup] 's' [VolumeDown] '[' [VolumeUp] ']'.\n");

    last_frame_time = SDL_GetTicks();

    //set the start time of the block
    startTime = SDL_GetTicks();
}

DisplayScreen::~DisplayScreen() {
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
        //manual_control_active = true;
    }
    manual_control_active = true;

}

void DisplayScreen::poll() {
    // manual_control_active = !manual_control_active;
    SDL_Event event;
    while(SDL_PollEvent(&event)) {
        handleSDLEvent(event);
    }
};

void DisplayScreen::manualSwitch() {
	manual_control_active = false;
	};

void DisplayScreen::handleSDLEvent(const SDL_Event& event) {
    switch (event.type) {
        case SDL_QUIT:
            exit(0);
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
        //manual_control_active = true;
        return UNDEFINED;
    }

    Action a = PLAYER_A_NOOP;
    poll();
    SDL_PumpEvents();
    Uint8* keymap = SDL_GetKeyState(NULL);

    // for mouse movement
    //int mdltx, mdlty;
    //auto r = SDL_GetRelativeMouseState(&mdltx, &mdlty);

    // Break out of this loop if the 'p' key is pressed
    if (keymap[SDLK_p]) {
      return PLAYER_A_NOOP;
      // MRI Pulse Actions
    } else if ((keymap[SDLK_5] && keymap[SDLK_SPACE]) || (keymap[SDLK_5] && keymap[SDLK_4])) {
      a = MRI_PULSE_FIRE;
    } else if ((keymap[SDLK_5] && keymap[SDLK_LEFT]) || (keymap[SDLK_5] && keymap[SDLK_1])) {
      a = MRI_PULSE_LEFT;
    } else if ((keymap[SDLK_5] && keymap[SDLK_RIGHT]) || (keymap[SDLK_5] && keymap[SDLK_2])) {
      a = MRI_PULSE_RIGHT;
    } else if (keymap[SDLK_5] && keymap[SDLK_UP]) {
      a = MRI_PULSE_UP;
    } else if (keymap[SDLK_5] && keymap[SDLK_DOWN]) {
      a = MRI_PULSE_DOWN;
    } else if (keymap[SDLK_5] && keymap[SDLK_SPACE] && keymap[SDLK_LEFT]) {
      a = MRI_PULSE_LEFTFIRE;
    } else if (keymap[SDLK_5] && keymap[SDLK_SPACE] && keymap[SDLK_RIGHT]) {
      a = MRI_PULSE_RIGHTFIRE;
    } else if (keymap[SDLK_5]){
      a = MRI_PULSE;
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
    } else if ((keymap[SDLK_LEFT] && keymap[SDLK_SPACE]) || (keymap[SDLK_1] && keymap[SDLK_4])) {
      a = PLAYER_A_LEFTFIRE;
    } else if ((keymap[SDLK_RIGHT] && keymap[SDLK_SPACE]) || (keymap[SDLK_2] && keymap[SDLK_4])) {
      a = PLAYER_A_RIGHTFIRE;
      // Single Actions
    } else if (keymap[SDLK_SPACE] || keymap[SDLK_4]) { ////|| keymap[SDLK_2] || keymap[SDLK_3] || !!(r&SDL_BUTTON(SDL_BUTTON_RIGHT)) || !!(r&SDL_BUTTON(SDL_BUTTON_LEFT))) {
      a = PLAYER_A_FIRE;
    } else if (keymap[SDLK_RETURN]) {
      a = PLAYER_A_NOOP;
    } else if (keymap[SDLK_LEFT] || keymap[SDLK_1]) {
      a = PLAYER_A_LEFT;
    } else if (keymap[SDLK_RIGHT] || keymap[SDLK_2]) {
      a = PLAYER_A_RIGHT;
    } else if (keymap[SDLK_UP]) {
      a = PLAYER_A_UP;
    } else if (keymap[SDLK_DOWN]) {
      a = PLAYER_A_DOWN;
    } else if (keymap[SDLK_b]){
      a = PROCEED;
    }
      else if (keymap[SDLK_q]){
      SDL_Quit();
    }
    
    return a;
}

#endif // __USE_SDL