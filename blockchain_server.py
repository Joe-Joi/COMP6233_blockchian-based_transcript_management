"""
author:
description:
api_path:
api_doc:
"""

import jsonpickle
import json
import rsa
import blockchain as bc
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
# Generate a globally unique address for this node


my_private_key = rsa.PrivateKey(
    96407792256974524720497783315958587334801655222575183423449541877569263981921160667294122718122130667197624597047093383678786490144457228529873281833027245765679205551891254663794956349370259791094946013896899522635884806014189143262539995794661370526147604520940131723333117256269971923100413906940288018387,
    65537,
    85035153260092304743779771157701788294788355917972764285455913724686343191463365938837665102823868735951079351464123779497626254623960427733919052778127955269664250311201912891669326931425329533195157120047113899956043299061025051906529044935721702165703166207701923842311644049920991271804598144288562133521,
    34040061605442737190253088458314803557893133037852935730051768113840214698860982149380991780950299353346961285400676907725682943409500607673814193257306637268405173,
    2832186186218878042072733401891502968995092012619738779106804824614590618679132778300096127325046776740835158793731172245087071050511276975663719)
my_public_key = rsa.PublicKey(
    96407792256974524720497783315958587334801655222575183423449541877569263981921160667294122718122130667197624597047093383678786490144457228529873281833027245765679205551891254663794956349370259791094946013896899522635884806014189143262539995794661370526147604520940131723333117256269971923100413906940288018387,
    65537)
public_address = my_public_key.__hash__()

blockchain = bc.Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine():
    new_block = blockchain.mine_records(public_address)
    print(f'{public_address} is the miner.')
    msg = {'msg': 'new block is mined', 'block_hash': new_block.hash, 'block_previousHash': new_block.previousHash}
    return jsonify(msg), 200


@app.route('/records/new', methods=['POST'])
def new_records():
    # check the existence of necessary information in the request
    record_info = request.get_json()

    necessary_info = ['school', 'student', 'transcript']
    for field in necessary_info:
        if field not in record_info.keys():
            return f'{field} is missing!', 400
    # the record is encrypted using school's public key
    encrypted_transcript = rsa.encrypt(json.dumps(record_info.get('transcript'), sort_keys=True).encode(),
                                       my_public_key).hex()
    record = bc.Record(record_info.get('school'), record_info.get('student'),
                       encrypted_transcript)

    # sign the record using school's private_key
    record.sign_records(my_private_key)
    blockchain.add_new_record(record)
    response = {'msg': f'a record from {record_info.get("school")} is added to chain'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def view_chain():
    # check the chain
    if request.args.get('object_dict') == 1:
        chain_dict = jsonpickle.encode(blockchain.chain)
    else:
        chain_dict = jsonpickle.encode(blockchain.chain, unpicklable=False, make_refs=False)
    response = {
        'chain': json.loads(chain_dict),
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/add_node', methods=['POST'])
def add_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Node name is necessary", 400

    for node in nodes:
        blockchain.add_node(node)

    response = {
        'message': 'Nodes have been added',
        'existing_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/consensus', methods=['GET'])
def consensus():
    is_updated = blockchain.make_consensus()

    if is_updated is True:
        response = {
            'message': 'Our chain was out of date and has been updated!',
            'new_chain': json.loads(jsonpickle.encode(blockchain.chain, unpicklable=False, make_refs=False))
        }
    else:
        response = {
            'message': 'Our chain is already the latest chain!',
            'chain': jsonpickle.encode(blockchain.chain, unpicklable=False, make_refs=False)
        }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
