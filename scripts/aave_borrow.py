from eth_typing import Address
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import config, network, interface
from web3 import Web3

AMMOUNT = Web3.toWei(0.01, "ether")


def main():
    # Initialize account and other
    account = get_account()
    weth_address = config["networks"][network.show_active()][
        "weth_token"
    ]  # Addres to ERC20 'version' of ETH

    # Get WETH - no need to get new WETH everytime You test it, it is already on a contract after first time, unless it's fork
    if network.show_active() == "mainnet-fork":
        get_weth()

    # Get the address of a contract to borrow from
    lending_pool = get_lending_pool()
    print(lending_pool)

    # # Approve sending ERC20 tokens to contract You want to borrow from
    # approve_erc20(AMMOUNT, lending_pool.address, weth_address, account)

    # # Deposit WETH on aave
    # print("Depositing..")
    # tx = lending_pool.deposit(
    #     weth_address, AMMOUNT, account.address, 0, {"from": account}
    # )
    # tx.wait(1)
    # print("Deposited!")

    # # Get data about your money situation
    # borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    # # DAI in terms of ETH (conversion)
    # dai_to_eth_price = get_asset_price(
    #     config["networks"][network.show_active()]["dai_eth_price_feed"]
    # )
    # amount_of_dai_to_borrow = (1 / dai_to_eth_price) * (
    #     borrowable_eth * 0.95
    # )  # 0.95 is to improve health factor
    # print(f"You will borrow {amount_of_dai_to_borrow} of Dai.")

    # # Borrow DAI
    # print("Let's borrow it..")
    # dai_address = config["networks"][network.show_active()]["dai_address"]
    # tx_borrow = lending_pool.borrow(
    #     dai_address,
    #     Web3.toWei(amount_of_dai_to_borrow, "ether"),
    #     1,
    #     0,
    #     account.address,
    #     {"from": account},
    # )
    # tx_borrow.wait(1)
    # print("You borrowed some DAI!")

    # # Check our aave related data after borrowing DAI
    # get_borrowable_data(lending_pool, account)

    # Repay DAI borrowed
    # check how much You can repay (assuming that 95% of what you borrowed is DAI)
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    dai_to_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_of_dai_to_repay = (1 / dai_to_eth_price) * (
        total_debt * 0.95
    )  # 0.95 cause I have BUSD borowed
    repay_all(amount_of_dai_to_repay, lending_pool, account)


def repay_all(amount, lending_pool, account):

    # Approve paying back
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_address"],
        account,
    )
    # Repay
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_address"],
        Web3.toWei(amount, "ether"),
        1,
        account,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed!")


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[
        1
    ]  # We are copying return with index 1 only
    converted_lates_price = Web3.fromWei(latest_price, "ether")
    print(f"DAI / ETH price is {converted_lates_price}")
    return float(converted_lates_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liqudation_treshload,
        ltv,
        heal_factor,
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    print(f"You have {available_borrow_eth} worth of ETH available to borrow.")

    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 tokens..")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )  # declare an object of this smart contract class
    lending_pool_addresses = (
        lending_pool_addresses_provider.getLendingPool()
    )  # use this object to get lending pool smart contract address
    # ABI
    # Address
    lending_pool = interface.ILendingPool(
        lending_pool_addresses
    )  # declare an object of lending pool class
    return lending_pool
