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

#ifndef DISPLAY_SCREEN_H
#define DISPLAY_SCREEN_H

#include <stdio.h>
#include <stdlib.h>

#include "Constants.h"
#include "ColourPalette.hpp"
#include "../emucore/MediaSrc.hxx"

#ifdef __USE_SDL
#include "SDL.h"

class DisplayScreen {
public:
    DisplayScreen(MediaSource* mediaSource, Sound* sound, ColourPalette &palette); 
    virtual ~DisplayScreen();

    // Displays the current frame buffer from the mediasource.
    void display_screen();

    // Has the user engaged manual control mode?
    bool manual_control_engaged() { return manual_control_active; }

    // switch manual control mode to false
    void manualSwitch();

    // Has the block ended?
    bool block_continue() { return block_on; }

    // Captures the keypress of a user in manual control mode.
    Action getUserAction();

protected:
    // Checks for SDL events.
    void poll();

    // Handle the SDL_Event.
    void handleSDLEvent(const SDL_Event& event);

protected:
    // Dimensions of the SDL window (4:3 aspect ratio)
    static const int window_height = 642; // can change this to set screen size LC 5/9/19
    static const int window_width = 856;
    // Maintains the paused/unpaused state of the game
    bool manual_control_active;
    bool block_on;
    MediaSource* media_source;
    Sound* my_sound;
    ColourPalette &colour_palette;
    int screen_height, screen_width;
    SDL_Surface *screen, *image;
    float yratio, xratio;
    Uint32 delay_msec;
    // Used to calibrate delay between frames
    Uint32 last_frame_time;
    Uint32 startTime;
};
#else
/** A dummy class that simply ignores display events. */
class DisplayScreen {
  public:
    DisplayScreen(MediaSource* mediaSource, Sound* sound, ColourPalette &palette) {}
    void display_screen() {}
    bool manual_control_engaged() { return false; }
    Action getUserAction() { return UNDEFINED; }
};
#endif // __USE_SDL

#endif // DISPLAY_SCREEN
