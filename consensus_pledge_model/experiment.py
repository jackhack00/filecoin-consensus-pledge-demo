from cadCAD_tools.execution import easy_run
from cadCAD_tools.preparation import sweep_cartesian_product
from consensus_pledge_model.types import GrowthScenario
import pandas as pd

from consensus_pledge_model.params import RAW_PARAMS


def standard_run() -> pd.DataFrame:
    from consensus_pledge_model import INITIAL_STATE, PARAMS, BLOCKS, TIMESTEPS, SAMPLES

    # Simulations
    # Set 1 of simulations: alternate growth scenarios

    # TODO: make sure that it matches the scoped experiment on alternate growth
    # scenarios
    set_1_args = (INITIAL_STATE, PARAMS, BLOCKS, TIMESTEPS, SAMPLES)
    set_1_df = easy_run(*set_1_args).assign(set='alternate_growth')

    # Set 2 of simulations: network power = baseline
    set_2_initial_state = INITIAL_STATE
    set_2_initial_state['network_power'] = set_2_initial_state['baseline']

    set_2_params = RAW_PARAMS.copy()
    set_2_params['baseline_activated'] = [True]
    set_2_params['network_power_scenario'] = [GrowthScenario('baseline')]
    set_2_params = sweep_cartesian_product(set_2_params)

    set_2_args = (set_2_initial_state, set_2_params,
                  BLOCKS, TIMESTEPS, SAMPLES) 
    set_2_df = easy_run(*set_2_args).assign(set='baseline')

    # Post Processing
    raw_df = pd.concat([set_1_df, set_2_df])

    dfs = [raw_df,
           raw_df.reward.map(lambda x: x.__dict__).apply(pd.Series),
           raw_df.network_power_scenario.map(lambda x: x.__dict__).apply(pd.Series)]

    DROP_COLS = ['reward', 'network_power_scenario']

    df = (pd.concat(dfs,
                    axis=1)
          .drop(columns=DROP_COLS)
          # .dropna()
          .set_index('days_passed')
          .assign(block_reward=lambda x: x.simple_reward + x.baseline_reward)
          .assign(marginal_reward=lambda x: x.block_reward / x.network_power)
          )

    # Mining Utility

    # TODO: make sure that it matches the expected dataset for the
    # visualizations
    agg_df = None

    return df # TODO use `agg_df` instead
