"""
author:
description:
api_path:
api_doc:
"""
import jsonpickle
import rsa
import blockchain as bc
import json
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

my_private_key = rsa.PrivateKey(
    115052274783034571192322482165612504610854827880237262769012553652009288070436508648603961059088220335392805986657072868325983803871103322220572478149179893127701437082982116775029260117971198771237997025876323375700317059076419371522020315320186154693607091173374131486359363544270152505030385197840579446649,
    65537,
    107433267618251776145636189344782160377656635210444173057589777466805200147191708802182226908967786439187536017294854636662423224216853228099125247920700435145161581810178425276054419378681877488715044019187006807098659275640715120425893560132262107276446942785229792574657048338875554737060274512596457593089,
    42033374470997393501161287584702963182390379152146567023573650435450712713791034967222085854487391222995827552398349225213507379410212831523981356271908235251895777,
    2737164841771613792765573088097653017671951383208795227286413830748920588491615286643275805117039133232308680772375102742274303732213212137667737)
my_public_key = rsa.PublicKey(
    115052274783034571192322482165612504610854827880237262769012553652009288070436508648603961059088220335392805986657072868325983803871103322220572478149179893127701437082982116775029260117971198771237997025876323375700317059076419371522020315320186154693607091173374131486359363544270152505030385197840579446649,
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
    app.run(host='0.0.0.0', port=5001)
