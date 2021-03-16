```
mkdir nlp_project/multi_process
mkdir nlp_project/multi_process/results
mkdir nlp_project/multi_process/configs

mkdir nlp_project/docs/outputs/tanda1
mkdir nlp_project/docs/outputs/tanda1/evaluation
mkdir nlp_project/docs/outputs/tanda1/training

mkdir nlp_project/docs/manual_corrections/tanda1
```

## copiar configs en nlp_project/multi_process/configs

```
scp nlp_project/scripts/configs/luisa_split/google/elmo_voc/* root@dev.ai.kona.tech:/root/xavi/luisa_split#google#own_voc/nlp_project/multi_process/configs
```

## copiar abbys 
```
scp nlp_project/docs/outputs/tanda1/test/* root@dev.ai.kona.tech:/root/xavi/luisa_split#google#own_voc/nlp_project/docs/outputs/tanda1/training
```

## copiar luisa que corresponda

```
scp nlp_project/LUISA/luisa_split/tanda1_test/* root@dev.ai.kona.tech:/root/xavi/luisa_split#google#own_voc/nlp_project/docs/manual_corrections/tanda1
```

## .ENV
```
nano .env
```


## GOOGLE
```
cd nlp_project/async_requests
npm i
pm2 start index.js --name xavi_requests
```


## VENV
```
cd ../../../
virtualenv -p python3.6 venv

source venv/bin/activate

cd [repo]
pip install -r requirements.txt

```


# START
```
cd nlp_project
pm2 start multi_process.py --name [xavi_tesis] --interpreter ../../venv/bin/python3.6 --log-date-format 'DD-MM HH:mm:ss'
```





# DE NUEVO
```
# LOCAL Y REMOTO
# split | join
luisa='split'
# google | billion
lm='billion'
# own | elmo
voc='elmo'

echo luisa_$luisa/$lm/"$voc"_voc


# REMOTO
git pull
cd nlp_project/multi_process
mv results/ $luisa#$lm#"$voc"_results
mkdir results
rm -f fin.txt
mkdir configs
rm -f configs/*

# REMOTO
cd ../../
cat .env

#Para saber si están los abbyy:
ls nlp_project/docs/outputs/tanda1/training

# REMOTO
#LUISA JOIN TIENE PRIORIDADES TODO JUNTO
cat nlp_project/docs/manual_corrections/tanda1/643_2236.1975.txt 
# O ELIMINAMOS LUISA PARA PASAR LO NUEVO y copiamos las nuevas
# REMOTO
rm -f nlp_project/docs/manual_corrections/tanda1/*
# LOCAL
scp nlp_project/LUISA/luisa_$luisa/* root@dev.ai.kona.tech:/root/xavi/luisa_$luisa#$lm#"$voc"_voc/nlp_project/docs/manual_corrections/tanda1/
# REMOTO
ls nlp_project/docs/manual_corrections/tanda1/ | wc -l
cat nlp_project/docs/manual_corrections/tanda1/643_2236.1975.txt 

# LOCAL
#COPIAR CONFIGS
ls nlp_project/scripts/configs/luisa_$luisa/$lm/"$voc"_voc/ | wc -l
scp nlp_project/scripts/configs/luisa_$luisa/$lm/"$voc"_voc/* root@dev.ai.kona.tech:/root/xavi/luisa_$luisa#$lm#"$voc"_voc/nlp_project/multi_process/configs

# Están bien las configs?
# REMOTO
ls nlp_project/multi_process/configs/ | wc -l
# Ver una config
cat nlp_project/multi_process/configs/config

# REMOTO
cd nlp_project
pm2 start multi_process.py --name $luisa#$lm#"$voc" --interpreter ../../venv/bin/python3.6 --log-date-format 'DD-MM HH:mm:ss'
```