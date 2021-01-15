# blockchain_demo

## Installation

### python version

the demo is based on Python3.8, recommend Python version > 3.6.

### pipenv

a packaging tool to manage virtual environments and dependency of Python project.

install pipenv
```bash
pip install pipenv 
```

create the virtual environment, and install the dependent packages.

```bash
pipenv install
```

## Project Guideline

### blockchain.py

blockchain.py contains Blockchain,Block,Transaction classes and related function，which is the basic demo。

### blockchain_server.py

after running the server, we can add records,mine records, make consensus&update blockchain by requesting the APIs.

#### /mine_block

GET request. Start solving the PoW puzzle to find a hash value whose first five characters are 0. 

#### /records/new

POST request. The format of request data should be json, and add `"Content-Type":"application/json"` to the request header. The school parameter is the hash value of the school's public address, and the student parameter is the hash value of the student's public_key. 

*Please make sure that the public key and corresponding hash value have been added to key_records.py file before sending request*

request data example：
```json
{
    "school": "7468873682774736652",
    "student": "8877551463833625084",
    "transcript": {
        "Data_science": "50"
    }
}
```

#### /chain

GET request. View the current status of chain.

#### /nodes/add_node


POST request. Register a node to the blockchain network. 

In our demo, we need to register nodes information below to both 5000 and 5001 node:

```json
{
  "nodes": [
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001"
  ]
}
```

#### /nodes/consensus

GET request. Compare all chains in registered nodes, and get the longest and validated chain.

### blockchain_server2.py

Totally same as the blockchain_server.py, except its running port and public_key. This is act as another node(school).

### key_records.py

In the blockchain network, the public key and its hash value is exposed to the network. The public key is needed to locate the school and verify the sign of records.

## 启动

Run blockchain_server.py and blockchain_server2.py in any order. If you can see the information below, you can request APIs via http://localhost:{port}.

```text
 * Debugger is active!
 * Debugger PIN: 156-243-903
 * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
```
