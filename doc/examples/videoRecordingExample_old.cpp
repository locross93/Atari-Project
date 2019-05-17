/* *****************************************************************************
 * A.L.E (Arcade Learning Environment)
 * Copyright (c) 2009-2013 by Yavar Naddaf, Joel Veness, Marc G. Bellemare,
 *  Matthew Hausknecht, and the Reinforcement Learning and Artificial Intelligence 
 *  Laboratory
 * Released under the GNU General Public License; see License.txt for details. 
 *
 * Based on: Stella  --  "An Atari 2600 VCS Emulator"
 * Copyright (c) 1995-2007 by Bradford W. Mott and the Stella team
 *
 * *****************************************************************************
 *  videoRecordingExample.cpp 
 *
 *  An example on recording video with the ALE. This requires SDL. 
 *  See manual for details. 
 **************************************************************************** */

#include <iostream>
#include <ale_interface.hpp>
#include <sstream>
#include <fstream>
#include <stdio.h>
#include <cstdlib>
#include <ctime>
#include <chrono>
#include <unistd.h>
#include <time.h>

#ifndef __USE_SDL
#error Video recording example is disabled as it requires SDL. Recompile with -DUSE_SDL=ON. 
#else

#include <SDL.h>

using namespace std;

// random generator function:
int myrandom (int i) { return std::rand()%i;}

int getUserInput() {

    int a = 0;
    SDL_PumpEvents();
    Uint8* keymap = SDL_GetKeyState(NULL);

    // for mouse movement
    //int mdltx, mdlty;
    //auto r = SDL_GetRelativeMouseState(&mdltx, &mdlty);

    // Break out of this loop if the 'p' key is pressed
    if (keymap[SDLK_p]) {
      return PLAYER_A_NOOP;
      // MRI Pulse Actions
    } else if (keymap[SDLK_5]){
      a = 2;
    } else if (keymap[SDLK_b]){
      a = 1;
    }
      else if (keymap[SDLK_q]){
      SDL_Quit();
    }
    
    return a;
}

int main(int argc, char** argv) {
    if (argc < 4) {
        std::cout << "Usage: " << argv[0] << " three rom_files" << std::endl;
        return 1;
    }

    //create a random sequence of what games to play 
    srand(time(NULL));
    int game_sequence[6] = {0, 1, 2, 0, 1, 2};
    bool loop = 0;
    while (loop==0){

        for (int i=5; i>0; --i) {
        swap (game_sequence[i],game_sequence[myrandom(i+1)]);
        }
        loop = 1;
        for (int j=0; j<5; ++j) {
            if (game_sequence[j] == game_sequence[j+1]){
                loop = 0;
            }
        }
    }

    for (int j=0; j<6; ++j) {
        std::cout << game_sequence[j];
    }
    std::cout << std::endl;

    ALEInterface ale;

    // Get & Set the desired settings
    ale.setInt("random_seed", 123);

    // We enable both screen and sound, which we will need for recording. 
    ale.setBool("display_screen", true);
    // You may leave sound disabled (by setting this flag to false) if so desired. 
    ale.setBool("sound", false);

    string subNum;
    std::cout << "Subject number: " << std::endl;
    std::cin >> subNum;
    std::cout << "You typed: " << subNum << std::endl;

    // loop over the 6 blocks of gameplay in a random sequence
    for (int j=0; j<6; ++j) {

    // get current time and create a string so folder can be timestamped
    time_t rawtime;
    struct tm * timeinfo;
    char buffer [80];

    time (&rawtime);
    timeinfo = localtime (&rawtime);

    strftime (buffer,80,"%m-%d_%I-%M",timeinfo);
    puts (buffer);

    // which game are we playing
    int game = game_sequence[j];

    //show cursor in between blocks
    SDL_ShowCursor(0);

    // convert loop and game numbers to string so folder can be marked by block and game type
    std::string loop_num = std::to_string(j+1);
    std::string game_num = std::to_string(game);

    std::string recordPath1 = "record/";
    std::string recordPathSub = recordPath1 + "sub" + subNum;
    // final path should look like: record/subject number/block number, game number, date, time 
    std::string recordPath = recordPath1 + "sub" + subNum + "/b" + loop_num + "g" + game_num + "_" + buffer;
    // std::string recordPath = recordPath1 + buffer;
    // recordPath2 << "record" << buffer;
    std::cout << recordPath << std::endl;

    // Set record flags
    ale.setString("record_screen_dir", recordPath.c_str());
    //ale.setString("record_sound_filename", (recordPath + "/sound.wav").c_str());
    // We set fragsize to 64 to ensure proper sound sync 
    ale.setInt("fragsize", 64);

    // Not completely portable, but will work in most cases
    std::string cmd = "mkdir ";
    cmd += recordPathSub; 
    system(cmd.c_str());
    std::string cmd2 = "mkdir ";
    cmd2 += recordPath; 
    system(cmd2.c_str());
    // loop over the 6 blocks of gameplay in a random sequence
    // for (int j=0; j<6; ++j) {
    // Load the ROM file. (Also resets the system for new settings to
    // take effect.)

    // record start time of the run before you proceed in actions.txt with 111
    std::ostringstream outFileName;
    std::ostringstream actionString;
    outFileName << recordPath << "/" <<  "actions.txt";
    actionString << "111," << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count() << ",99" << ",99" << std::endl;
    std::ofstream actFile(outFileName.str(), std::ios_base::app);
    actFile << actionString.str();
    actFile.close();

    // uncomment below for full screen 
    SDL_Surface *screen;
    screen = SDL_SetVideoMode(428, 321, 8, SDL_HWPALETTE);
    // uncomment below for full screen 
    // screen = SDL_SetVideoMode(428, 321, 8, SDL_HWPALETTE | SDL_FULLSCREEN);

    if (screen == NULL) {
        fprintf(stderr, "Couldn't Initialize Screen: %s\n", SDL_GetError());
        exit(1);
    }

    // Load the image
    SDL_Surface* image = NULL;
    image = SDL_LoadBMP("fixation_cross.bmp");
    //Create an optimized image
    SDL_Surface* optimizedImage = NULL;
    optimizedImage = SDL_DisplayFormat(image);
        
    //Free the old image
    SDL_FreeSurface(image);

    // Apply the image to the display
    //if (SDL_BlitSurface(optimizedImage, NULL, screen, NULL) != 0)
    //{   
    //    fprintf(stderr, "Couldnt blit \n");
    //    exit(1);
    //}

    //commented out for debugging 4/30/19
    bool loop=0;
    while(loop == 0){
        if (getUserInput() == 1){
            fprintf(stderr, "Ready for MRI Pulse... \n");
            while(loop == 0){
                if (getUserInput() == 2){
                    //put on the fixation cross
                    screen = SDL_SetVideoMode(428, 321, 8, SDL_HWPALETTE | SDL_FULLSCREEN);
                    SDL_ShowCursor(0);
                    if (SDL_BlitSurface(optimizedImage, NULL, screen, NULL) != 0)
                    {   
                        fprintf(stderr, "Couldnt blit \n");
                        exit(1);
                    }
                    SDL_Flip(screen);
                    //sleep_for(nanoseconds(10));
                    //std::this_thread::sleep_for(std::chrono::milliseconds(10000));
                    //for (int j=0; j<6; ++j)
		     //commented out for debugging 4/30/19
                    //usleep(60000000);
                    //}
                    loop = 1;
                }
            }
        }
    }

    // mark when a the first fixation cross ends with 222
    std::ostringstream actionString2;
    actionString2 << "222," << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count() << ",99" << ",99" << std::endl;
    std::ofstream actFile2(outFileName.str(), std::ios_base::app);
    actFile2 << actionString2.str();
    actFile2.close();

    // load the ROM for the current game in the block
    ale.loadROM(argv[game + 1]);

    // Get the vector of legal actions
    ActionVect legal_actions = ale.getLegalActionSet();

    // Play a single or more episodes, which we record. 
    while (ale.block_over()) {
        
        Action a = legal_actions[rand() % legal_actions.size()];
        // Apply the action (discard the resulting reward)
        ale.act(a);

    if (ale.game_over()){
        ale.reset_game();
        // mark when a new game starts with 555
        std::ostringstream actionString3;
        actionString3 << "555," << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count() << ",99" << ",99" << std::endl;
        std::ofstream actFile3(outFileName.str(), std::ios_base::app);
        actFile3 << actionString3.str();
        actFile3.close();
    }
    }

    std::cout << std::endl;
    // mark when a block ends with 999
    std::ostringstream actionString4;
    actionString4 << "999," << std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count() << ",99" << ",99" << std::endl;
    std::ofstream actFile4(outFileName.str(), std::ios_base::app);
    actFile4 << actionString4.str();
    actFile4.close();
    }
    return 0;
}
#endif // __USE_SDL
