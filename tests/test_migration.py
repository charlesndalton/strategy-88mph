# TODO: Add tests that show proper migration of the strategy to a newer one
#       Use another copy of the strategy to simulate the migration
#       Show that nothing is lost!

import pytest


def test_migration(
        chain,
        token,
        vault,
        strategy,
        amount,
        Strategy,
        strategist,
        gov,
        user,
        RELATIVE_APPROX,
        pool,
        stakeToken,
        tradeFactory,
        min):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    chain.sleep(1)
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount

    # migrate to a new strategy
    new_strategy = strategist.deploy(Strategy, vault, pool, stakeToken, tradeFactory)

    new_strategy.setOldStrategy(strategy, {'from': gov})
    new_strategy.setMinWithdraw(min[0], {'from': gov})
    new_strategy.setDust(min[1], {'from': gov})
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})

    assert (
            pytest.approx(new_strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount
    )

    # harvest to make sure nft ownerships were transferred correctly
    new_strategy.harvest()
