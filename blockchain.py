"""
author:
description:
api_path:
api_doc:
"""
import hashlib
from urllib.parse import urlparse
from datetime import datetime
import rsa
import requests
import jsonpickle
import key_records


class Block:
    def __init__(self, records, previousHash):
        self.records = records
        self.previousHash = previousHash
        self.nonce = 0
        self.timestamp = datetime.now()
        self.hash = self.get_hash()

    def get_hash(self):
        return hashlib.sha256(
            f'{self.records}{self.previousHash}{self.timestamp}{self.nonce}'.encode()).hexdigest()

    def mine(self, difficulty_level=5):
        # verify whether these records are validated before mining
        if self.validate_records() is False:
            print('some records are invalidated, stop mining!')
            return False
        else:
            # mine a block by using the POW algorithm
            answer = ""
            for i in range(difficulty_level):
                answer += '0'
            print(self.hash)
            while (self.hash[0: difficulty_level] == answer) is False:
                self.nonce += 1
                self.hash = self.get_hash()
            print(f'finish mining, you found a new block : {self.hash}')

    def validate_records(self):
        for record in self.records:
            if not record.verify_sign():
                return False
        return True


class Record:
    def __init__(self, school, student, transcript):
        self.school = school
        self.student = student
        self.transcript = transcript
        self.signature = None

    def get_hash(self):
        return hashlib.sha256(f'{self.student}{self.school}{self.transcript}'.encode()).hexdigest()

    def sign_records(self, private_key):
        self.signature = rsa.sign(self.get_hash().encode(), private_key, 'SHA-256')
        print(self.signature)

    def verify_sign(self):
        # validate the signature, if the school is '', it means this is a reward transaction for mining data, then True.
        if self.school == '':
            return True
        elif self.signature is None:
            return False
        else:
            # get public key from key_records file using the public_address(hash)
            for record in key_records.school_list:
                if self.school == record.get('hash'):
                    public_key = rsa.PublicKey(*record.get('public_key'))
            if public_key:
                try:
                    rsa.verify(self.get_hash().encode(), self.signature, public_key)
                except rsa.pkcs1.VerificationError:
                    return False

            else:
                print('User not found!')
                return False
        return True


class Blockchain(object):
    def __init__(self):
        # generate a first block with empty record and add it to chain.
        first_block = Block([], '0')
        self.chain = [first_block]
        self.stored_records = []
        self.nodes = set()
        print(self.chain)

    def add_node(self, node_address):
        # add a node to node list
        parsed_url = urlparse(node_address)
        self.nodes.add(parsed_url.netloc)

    def add_new_block(self, record, previousHash=None):
        # create a new block
        block = Block(record, previousHash or self.chain[-1].get('hash'))
        self.chain.append(block)

    def mine_records(self, miner_address):
        # this reward transaction is for people who have mined a block successfully, so the sender address is empty
        reward_transaction = Record('', miner_address, 'reward_record')
        self.stored_records.append(reward_transaction)

        # mining
        new_block = Block(self.stored_records, self.chain[-1].hash)
        new_block.mine()
        self.chain.append(new_block)
        self.stored_records = []
        return new_block

    def add_new_record(self, *records):
        for record in records:
            # Adds a new record to the list of records
            if record.school and record.student and record.transcript:
                self.stored_records.append(record)
            else:
                print('necessary information is missing!')

    def validate_chain(self):
        # validate whether each block has not been tampered, and the previousHash value is the previous block
        if len(self.chain) == 1:
            if self.chain[0].hash != self.chain[0].get_hash():
                return False
        else:
            for block_index in range(1, len(self.chain)):
                if self.chain[block_index].previousHash != self.chain[block_index - 1].hash:
                    print('the chain is broken!')
                    return False
                if self.chain[block_index].hash != self.chain[block_index].get_hash():
                    print('the data in block_chain has been tampered!')
                    return False
                if self.chain[block_index].validate_records() is not True:
                    print('the records is invalidated!')
                    return False
                else:
                    print('validation passed!')
                    return True

    def make_consensus(self):
        current_nodes = self.nodes
        new_chain = None
        our_length = len(self.chain)
        for node in current_nodes:
            print(f'I am going to request http://{node}/chain')
            # get object_dict
            res = requests.get(f'http://{node}/chain?object_dict=1')
            if res.status_code == 200:
                length = res.json()['length']
                chain = res.json()['chain']
                for index, block_str in enumerate(chain):
                    try:
                        chain[index] = jsonpickle.decode(block_str)
                    except:
                        print(block_str)

                if length > our_length and self.validate_chain():
                    our_length = length
                    new_chain = chain
            else:
                print('Request fail!')
        if new_chain:
            self.chain = new_chain
            return True
        return False


if __name__ == '__main__':
    my_private_key = rsa.PrivateKey(
        96407792256974524720497783315958587334801655222575183423449541877569263981921160667294122718122130667197624597047093383678786490144457228529873281833027245765679205551891254663794956349370259791094946013896899522635884806014189143262539995794661370526147604520940131723333117256269971923100413906940288018387,
        65537,
        85035153260092304743779771157701788294788355917972764285455913724686343191463365938837665102823868735951079351464123779497626254623960427733919052778127955269664250311201912891669326931425329533195157120047113899956043299061025051906529044935721702165703166207701923842311644049920991271804598144288562133521,
        34040061605442737190253088458314803557893133037852935730051768113840214698860982149380991780950299353346961285400676907725682943409500607673814193257306637268405173,
        2832186186218878042072733401891502968995092012619738779106804824614590618679132778300096127325046776740835158793731172245087071050511276975663719)

    test_chain = Blockchain()
    record1 = Record('7468873682774736652', '8877551463833625084',
                     "81919b6479d2b4064682098b541df1f143afdc78b35f820857203e2093f055c299d67ab97500dab4d32c09831637f1092f1af7469003b41ea244952df8b6afe8e9c1d92a48e5b559388a002a1cf12cbd977a35c46c7468473830e96c1cc060ec7d2027ad242b38a57379f495ec8b599a772c8a4080e5ae7fb968ab4404e4a014")
    record1.sign_records(my_private_key)
    test_chain.add_new_record(record1)
    # print(record1.__dict__)
    test_chain.mine_records('7468873682774736652')
    # test_chain.add_new_record(record1)
    # test_chain.mine_records('1667712905488965557')
    # print(test_chain.__dict__)
    # for block in test_chain.chain:
    #     print(block.__dict__)
    #     if isinstance(block.records, list):
    #         for transaction in block.records:
    #             print(transaction.__dict__)

    # test_chain.validate_chain()
    # secured_chain = Blockchain()
    # (public_sender, private_sender) = rsa.newkeys(1024)
    # (public_receiver, private_recevier) = rsa.newkeys(1024)
    # transaction1 = Transaction(public_sender, public_receiver, 10)
    # transaction1.sign_transactions(private_sender)
    # transaction2 = Transaction(public_receiver, public_sender, 8)
    # transaction2.sign_transactions(private_recevier)
    # secured_chain.add_new_transaction(transaction1, transaction2)
    # secured_chain.mine_transactions(public_sender)
    # for block in secured_chain.chain:
    #     pprint(block.__dict__)
    # secured_chain.validate_chain()
