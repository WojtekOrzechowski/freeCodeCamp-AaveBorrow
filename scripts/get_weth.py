from scripts.helpful_scripts import get_account
from brownie import interface, config, network
from web3 import Web3


def main():
    get_weth()


def get_weth():
    """
    Mint WETH by depositing ETH.
    """
    # ABI
    # Contract
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": Web3.toWei(0.02, "ether")})
    tx.wait(1)
    print("Received 0.02 WETH")
    # return tx
