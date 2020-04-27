# Blockchain for supply chain management

**Undergoing major overhaul check back in few days**

Note: Please have a glance over the sawtooth hyperledger architecture to make more sense out of this document.

## Introduction

This repository contains a web app that can be hosted on your ubuntu machine that talks with a sawtooth network. We defined few transaction families for our use, and those will be running on the validator node (More documentation to come explaining the transaction families).This project depends on

* Hyperledger sawtooth on Ubuntu 16.04
* Django 2.0 or later
* git
* screen (optional)

## Installation Procedure

### Installation with Docker

Make sure that you install Docker and Docker-compose(For Windows and Mac installing docker will also install docker-compose).After installing download [docker-compose.yaml](https://github.com/GuyFawkes1/supplychain/blob/webapp/docker/docker-compose.yaml) and run docker-compose up.

### Using Native Ubuntu

#### Installation of hyperledger-sawtooth

```shell
user@validator$ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD
user@validator$ sudo add-apt-repository 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/1.0/stable xenial universe'
user@validator$ sudo apt-get update
user@validator$ sudo apt-get install -y sawtooth
```

#### Generate User Key and validator key

Generate an user key with

```shell
user@validator$ sawtooth keygen
```

Generate a validator private key with

```shell
user@validator$ sudo sawadm keygen
```

#### Genesis block creation

Now since this is the first validator, we need to create the first block in the blockchain (Genesis block). All the commands in this subsection are to run only on the first node. 

```shell
$ sudo sawset genesis -k /etc/sawtooth/keys/validator.priv -o config-genesis.batch

$ sudo sawset proposal create -k /etc/sawtooth/keys/validator.priv \
-o config.batch \
sawtooth.consensus.algorithm=poet \
sawtooth.poet.report_public_key_pem="$(cat /etc/sawtooth/simulator_rk_pub.pem)" \
sawtooth.poet.valid_enclave_measurements=$(poet enclave measurement) \
sawtooth.poet.valid_enclave_basenames=$(poet enclave basename)

$ sudo poet registration create -k /etc/sawtooth/keys/validator.priv -o poet.batch

$ sudo sawset proposal create -k /etc/sawtooth/keys/validator.priv \
-o poet-settings.batch \
sawtooth.poet.target_wait_time=5 \
sawtooth.poet.initial_wait_time=25 \
sawtooth.publisher.max_batches_per_block=100

$ sudo sawadm genesis config-genesis.batch config.batch poet.batch poet-settings.batch
```

Note:To make a better sense out of the above steps please refer [Sawtooth Documentation](https://sawtooth.hyperledger.org/docs/core/nightly/master/app_developers_guide/creating_sawtooth_network.html)

#### Starting the first validator

Before we start the first validator, since we are creating a network of validators, find out the local ip of the machine and its public endpoint.Now start the validator with

```shell
sudo -u sawtooth sawtooth-validator -v \
    --bind network:tcp://(your local ip):8800 \
    --bind component:tcp://127.0.0.1:4004 \
    --peering dynamic \
    --endpoint tcp://(your public endpoint):8800 \
    --scheduler parallel \
    --network trust
```

Note: you can also add the peers here by the flag --peers tcp://(public endpoint of the second machine):8800

#### Adding rest api and default transaction processors

Open a new terminal window (or a screen session) and start the rest-api of sawtooth framework with:

```shell
$ sudo -u sawtooth sawtooth-rest-api -v
```

On a new terminal window start the following transaction processors:

```shell
$ sudo -u sawtooth settings-tp -v
```

```shell
$ sudo -u sawtooth poet-validator-registry-tp -v
```

##### Note: keep all the terminals open or send them to  the background using '&'


#### Getting this repo, starting the custom transaction processors and django

git the repo into your file system and start the tps.

```shell
git clone https://github.com/GuyFawkes1/supplychain.git
python3 supplychain/Transaction_Families/sawtooth/proc/main.py tcp://127.0.0.1:4004
python3 supplychain/Transaction_Families/wallet_tf/proc/main.py tcp://127.0.0.1:4004
python3 supplychain/webapp/manage.py runserver 0:8000
```
Now go to your public_ip:8000/items/home and you can see the application up and running

#### Setting up second node(machine)

Install sawtooth as above and then start the validator with :

```shell
sudo -u sawtooth sawtooth-validator -v \
    --bind network:tcp://(your local ip):8800 \
    --bind component:tcp://127.0.0.1:4004 \
    --peering dynamic \
    --endpoint tcp://(your public endpoint):8800 \
    --seeds tcp://(public ip of the first validator):8800 \
    --scheduler parallel \
    --network trust
```

##### If seeds doesnot work, try using --peers (public ip of the first validator)

Now start the rest-api, default tps and custom tps as above

```shell
$ sudo -u sawtooth sawtooth-rest-api -v
```

On a new terminal window start the following transaction processors:

```shell
$ sudo -u sawtooth settings-tp -v
```

```shell
$ sudo -u sawtooth poet-validator-registry-tp -v
```

```shell
git clone https://github.com/GuyFawkes1/supplychain.git
python3 supplychain/Transaction_Families/sawtooth/proc/main.py tcp://127.0.0.1:4004
python3 supplychain/Transaction_Families/wallet_tf/proc/main.py tcp://127.0.0.1:4004
```

#### Troubleshooting

* Every tp must be started in a new terminal

* Make sure you give sawtooth permission to access /var/lib/sawtooth.

```shell
sudo chmod 777 -R /var/lib/sawtooth
```
Make sure that you add your public ip to the allowed hosts in the django settings.py

#### Shortcut method (experimental, may raise errors)

Install sawtooth and create the genisis block as described above.Then git clone this repo to your home diectory and then run the script settingupsaw.sh.(Make sure you edit the details the script)

#### Getting rid of all the block chain data to start a new chain

Navigate to /var/lib/sawtooth and delete all the files inside it. To create a new blockchain follow the same procedure as above, from starting the first validator (if you don't want to change any settings of poet else you have to start from creating the genesis block)



## Details of folders

### Transaction Families

This folder cointains all the transaction processors in the current project. There are two transaction processors in the current project : sawtooth and wallet_tf. Each of the folders then have a **proc** folder and few scripts that can be run directly on the machine running the sawtooth validator (For debugging or other purposes). The proc folder then contains a transaction handler (smart contract equivalent), a script that takes care of state assignments and another script to unpack a transaction's payload.(Currently the payload is base64 encoded but in future we can add some encryption to it if necessary)

### Webapp

This folder has the django project that is used to host the current Active Release Platform. All the wrapping of transactions and creations are handled inside the items app of this project.

### RESTAPI

This folder contains an incomplete rest api. Currently not under development.
