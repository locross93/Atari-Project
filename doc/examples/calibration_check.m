clear all;
%Input subject number and run number
subID = input('Subject number: ');
run_num = input('Run number: ');

% 0 if on desktop 1 if on scanner
var.real = 1;
var.eyetrack = 0;

%Find which game we are playing this block and make a string for the ALE
%code
data_file = ['record/sub_',num2str(subID),'gameSequence'];
load(data_file)
game_num = game_blocks(run_num);
if game_num == 0
    game = 'enduro.bin';
elseif game_num == 1
    game = 'pong.bin';
elseif game_num == 2
    game = 'space_invaders.bin';
end

ale_code = ['./videoRecordingExample ',game,' ',num2str(run_num),' ',num2str(subID),' &']

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
    %Screen('BlendFunction', wPtr, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    %5Screen('FillRect',0, [0 0 0 100], [1680 0 2960 1024]);
else
    %[wPtr,rect] = Screen('OpenWindow',0, [100 100 100], [20 20 500 500]);
    [wPtr,rect] = Screen('OpenWindow',0, [100 100 100], [1680 0 2960 1024]);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% INITIALIZE EYELINK (EL) EYETRACKR
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
    edfFile = [num2str(subID),'r',num2str(run_num),'.edf'];
    Eyelink('Openfile', edfFile);
    
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CALIBRATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if var.eyetrack
    
    disp('here 1')
    
    %showInstruction(wPtr,'instructions/calibrationStart.txt') % we want participant to evaluate the images after each blockq
    WaitSecs(0.4);
%     while 1
%         
%         [down, secs, keycode] = KbCheck(-3,2);
%         keyresp = find(keycode);
%         if ismember (keyresp, mri_key)
%             disp('Started')
%             break
%         end
%         
%     end
    
    % Calibrate the eye qtracker
    EyelinkDoTrackerSetup(el);
    % do a final check of calibration using driftcorrection
    success = EyelinkDoDriftCorrection(el);
    disp('here 2')
    if success~=1
         Eyelink('Shutdown');sca;
        disp('Eyelink calibration failed.');
        return;
    end
    disp('here 3')
    
end

Screen('FillRect', wPtr, [255 255 255]); % reset blackground
Screen(wPtr,'Flip');
disp('Calibration Complete')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% START EXPERIMENT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

triggerscanner = 0;

%close and make new window
sca;
%mask the top taskbar and ALE title bar
[wpt, rect] = Screen('OpenWindow', 0, [0 0 0], [0 0 1400 52]);

disp('Waiting for MRI Pulse')

setenv('alecommand', ale_code)
!$alecommand &

WaitSecs(0.4);
while ~triggerscanner
    [down, secs, keycode, d] = KbCheck(-3,2);
    keyresp = find(keycode);
    if (down == 1)
        if ismember (keyresp, mri_key)
            triggerscanner = 1;
        end
    end
    %WaitSecs(.01);
end

start_time = GetSecs();
ref_end = 0;

disp('Starting Experiment')

if var.eyetrack
    Eyelink('StartRecording');
    Eyelink('Message', 'SYNCTIME');  % mark zero-plot time in data file
    Eyelink('Message', 'START EXPERIMENT'); % mark experiment start 
else
    data.timeStamp.absStart = java.lang.System.nanoTime/1000000000; % unixformat (if you are happy with that then remove the java timestampS
end

%while GetSecs() - start_time < 600
while GetSecs() - start_time < 90  
    [secs, keyCode, deltaSecs] = KbWait(-1);
    if any(keyCode(mri_key))
        current_time = num2str(GetSecs());
        disp('5 pressed')
        if var.eyetrack
            Eyelink('Message', ['TIME' ' ' current_time]); %%has to be a string % message is the system time
        end
    elseif any(keyCode(quit_key))
        break 
    end
end

if var.eyetrack % close and save eyelink
    
    Eyelink('StopRecording')
    Eyelink('CloseFile');
    status = Eyelink('ReceiveFile'); % download file 
    Eyelink('Shutdown');
    
end



