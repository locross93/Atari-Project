%Input subject number
subID = input('Subject number: ');

%Randomize the sequence of games with the condition of not playing the same
%game twice in a row
game_sequence = [0 1 2 0 1 2];

loop = 0;
while loop == 0
    perm = randperm(6);
    game_blocks = game_sequence(perm);
    loop = 1;
    for i=1:5
        if game_blocks(i) == game_blocks(i+1)
            loop = 0;
        end
    end
end

%save the sequence in a mat file for this subject
data_file = ['record/sub_',num2str(subID),'gameSequence'];
save(data_file,'game_blocks')