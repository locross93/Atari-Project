%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%1. Run initialize_subject_1day.m (or 2day)
%2. Run calibrate_subj.m
%3. Run run_game.m
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


clear all;
%Input subject number and run number
subID = input('Subject number: ','s');
%day_num = input('Day number: ');

% 0 if on desktop 1 if on scanner
var.real = 1;
var.eyetrack = 1;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PRELIMINARY STUFF
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

AssertOpenGL; % Check for Opengl compatibility, abort otherwise:
KbName('UnifyKeyNames');% Make sure keyboard mapping is the same on all supported operating systems (% Apple MacOS/X, MS-Windows and GNU/Linux)
KbCheck; WaitSecs(0.1); GetSecs; FlushEvents; % clean the keyboard memory% Do dummy calls to GetSecs, WaitSecs, KbCheck to make sure they are loaded and ready when we need them - without delays
mri_key = [KbName('5'), KbName('5%')];
quit_key = [KbName('q')];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% open PTS
PsychDefaultSetup(1);% Here we call some default settings for setting up PTB
if var.real == 1
    %change this 
    [wPtr,rect] = Screen('OpenWindow',0, [100 100 100], [0 0 1400 1050]);
else
    [wPtr,rect] = Screen('OpenWindow',0, [100 100 100], [1680 0 2960 1024]);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% INITIALIZE EYELINK (EL) EYETRACKER
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if var.eyetrack
    
    
    el=EyelinkInitDefaults(wPtr); % give to EL details about graphic enviroment
    
    dummymode = 0; % initialize connection to EL gaze tracker
    if ~EyelinkInit(dummymode, 1)
        fprintf('Eyelink Init aborted.\n');
        Eyelink('Shutdown');sca; % close all if it does not work
        return;
    end
    
    % Retrieve eye tracker version.
    [~, vs]=Eyelink('GetTrackerVersion');
    fprintf('Running experiment on a ''%s'' tracker.\n', vs);
    % make sure that we get gaze data from the Eyelink
    Eyelink('Command', 'link_sample_data = LEFT,RIGHT,GAZE,AREA'); 
    % open file to record data to
    edfFile = [subID(1:3),'d',subID(end),'.edf'];
    %edfFile = [num2str(subID),'d',num2str(day_num),'.edf'];
    Eyelink('Openfile', edfFile);
    
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CALIBRATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if var.eyetrack
    
    % Calibrate the eye tracker
    EyelinkDoTrackerSetup(el);
    % do a final check of calibration using driftcorrection
    success = EyelinkDoDriftCorrection(el);
    disp('here 2')
    if success~=1
         Eyelink('Shutdown');sca;
        disp('Eyelink calibration failed.');
        return;
    end
   
end

Screen('FillRect', wPtr, [255 255 255]); % reset blackground
Screen(wPtr,'Flip');
disp('Calibration Complete')