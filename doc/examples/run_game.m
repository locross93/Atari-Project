%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%1. Run initialize_subject_1day.m (or 2day)
%2. Run calibrate_subj.m
%3. Run run_game.m for every run
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Input subject number and run number
subID = input('Subject number: ','s');
run_num = input('Run number: ');

% 0 if on desktop 1 if on scanner
var.real = 1;
var.eyetrack = 1;

% if you want to save one run at a time, and recalibrate after
save_ind_run = 0;

%how long is the scan time
scan_time = 598; % stop early so last pulse breaks out of loop

%Find which game we are playing this block and make a string for the ALE
%code
data_file = ['record/sub_',subID,'gameSequence'];
load(data_file)
game_num = game_blocks(run_num);
if game_num == 0
    game = 'enduro.bin';
elseif game_num == 1
    game = 'pong.bin';
elseif game_num == 2
    game = 'space_invaders.bin';
end

ale_code = ['./videoRecordingExample ',game,' ',num2str(run_num),' ',subID,' &']

%is this the last run for the day
first_run = 0;
last_run = 0;
if run_num == 1
    first_run = 1;
elseif length(game_blocks) == run_num
    last_run = 1;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PRELIMINARY STUFF
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

AssertOpenGL; % Check for Opengl compatibility, abort otherwise:
KbName('UnifyKeyNames');% Make sure keyboard mapping is the same on all supported operating systems (% Apple MacOS/X, MS-Windows and GNU/Linux)
KbCheck; WaitSecs(0.1); GetSecs; FlushEvents; % clean the keyboard memory% Do dummy calls to GetSecs, WaitSecs, KbCheck to make sure they are loaded and ready when we need them - without delays
mri_key = [KbName('5'), KbName('5%')];
quit_key = [KbName('q')];

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
end

start_time = GetSecs();
ref_end = 0;

disp('Starting Experiment')

if var.eyetrack && first_run
    Eyelink('StartRecording');
    Eyelink('Message', 'SYNCTIME');  % mark zero-plot time in data file
    %Eyelink('Message', 'START EXPERIMENT'); % mark experiment start 
    Eyelink('Message', ['STARTING RUN' ' ' num2str(run_num)]); % mark run start 
elseif var.eyetrack
    Eyelink('Message', 'SYNCTIME');  % mark zero-plot time in data file
    %Eyelink('Message', 'START EXPERIMENT'); % mark experiment start 
    Eyelink('Message', ['STARTING RUN' ' ' num2str(run_num)]); % mark run start
end


while GetSecs() - start_time < scan_time 
    %for every key board press, check if its a 5 and send trigger 
    %then check if 600s have passed and break out of loop 
    %if stuck in loop after 600s, press any button
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

if var.eyetrack && last_run % if last run, close and save eyelink
    
    disp('Saving Eyelink file after last run')
    Eyelink('StopRecording')
    Eyelink('CloseFile');
    status = Eyelink('ReceiveFile'); % download file 
    Eyelink('Shutdown');
    
end

if var.eyetrack && save_ind_run % if you want to save one run at a time, close and save eyelink
    
    disp('Saving Eyelink file after last run')
    Eyelink('StopRecording')
    Eyelink('CloseFile');
    status = Eyelink('ReceiveFile'); % download file 
    Eyelink('Shutdown');
    
end