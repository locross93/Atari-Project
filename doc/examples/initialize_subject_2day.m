%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%1. Run initialize_subject_1day.m (or 2day)
%2. Run calibrate_subj.m
%3. Run run_game.m for every run
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Input subject number
subID = input('Subject number: ','s');

%Randomize the sequence of games with the condition of not playing the same
%game twice in a row
game_sequence = [0 1 2 0 1 2 0 1 2];

loop = 0;
while loop == 0
    perm = randperm(9);
    game_blocks = game_sequence(perm);
    loop = 1;
    for i=1:8
        if game_blocks(i) == game_blocks(i+1)
            loop = 0;
        end
    end
end

%save the sequence in a mat file for this subject
disp(game_blocks)
data_file = ['record/sub_',subID,'gameSequence'];
save(data_file,'game_blocks')