cd record

folders = dir;
folders = folders(5:length(folders));

act_matrix = zeros(1,129);

for i=1:length(folders)
    actions = readtable([folders(i).name,'/actions.txt']);
    actions(1,:) = [];
    actions = actions(:,3);
    actions = table2array(actions);
    
    RAM = readtable([folders(i).name,'/RAM.txt']);
    RAM(1,:) = [];
    RAM(:,129) = [];
    temp_string = RAM(:,1);
    RAM = [zeros(size(RAM,1),1) table2array(RAM(:,2:128))];
    temp_string = table2array(temp_string);
    temp_string = char(temp_string);
    temp_int = zeros(size(temp_string,1),1);
    
    for j=1:size(temp_string,1)
        for k=1:size(temp_string,2)
            if temp_string(j,k) == ':'
                temp_int(j) = str2num(temp_string(j,(k+1):size(temp_string,2)));
            end
        end
    end
    
    RAM(:,1)=temp_int;
    
    if i == 1
        act_matrix = [actions RAM];
    else
        matrix_temp = [actions RAM];
        act_matrix = [act_matrix; matrix_temp];
    end
end

cd ..

BaggedEnsemble = TreeBagger(50,act_matrix(:,2:129),act_matrix(:,1),'OOBPrediction','On',...
    'OOBVarImp','On','Method','classification')

oobErrorBaggedEnsemble = oobError(BaggedEnsemble);
figure
plot(oobError(BaggedEnsemble))
xlabel 'Number of Grown Trees'
ylabel 'Out-of-Bag Mean Squared Error'

figure
bar(BaggedEnsemble.OOBPermutedVarDeltaError)
xlabel 'Feature Number'
ylabel 'Out-of-Bag Feature Importance'