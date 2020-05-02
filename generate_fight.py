import json
import pandas as pd
from tabulate import tabulate
from itertools import combinations_with_replacement


def get_first_suitable(xs, condition):
    for x in xs:
        if condition(x):
            return x
    return x[-1]


def get_danger_booster(n_heroes, n_monsters):
    with open('config/multipliers.json') as fp:
        xss = json.load(fp)
    xs = get_first_suitable(xss.keys(), lambda x: int(x) >= n_heroes)
    x = get_first_suitable(xss[xs].keys(), lambda x: int(x) >= n_monsters)
    return xss[xs][x]


def get_combinations(danger, number, experience):
    df = pd.DataFrame({'combinations': list(combinations_with_replacement(danger, number))})
    df['sum'] = df['combinations'].apply(sum)
    df = df[df['sum'] <= experience]
    return df


def print_output(**kwargs):
    with open("config/output_format") as fp:
        output = fp.read().format(**kwargs)
        print(output)
        return output


def input_handle(name, invintation, target_type, defaults):
    default = defaults.get(name)
    if default:
        invintation += ' (' + str(default) + '): '
    else:
        invintation += ': '
    return target_type(input(invintation) or default)


def generate_fight(experience, n_strong, n_weak, n_heroes=4, insignificance_threshold=0.15):
    danger_booster = get_danger_booster(n_heroes, n_strong)
    threshold = insignificance_threshold * experience
    exp_corrected = experience / danger_booster
    
    danger = list(pd.read_csv("config/danger.csv", names=['value'], header=None)['value'])
    strong = list(filter(lambda x: threshold < x <= exp_corrected, danger))
    weak = list(filter(lambda x: x <= threshold, danger))
    
    df_strong = get_combinations(strong, n_strong, exp_corrected)
    df_weak = get_combinations(weak, n_weak, exp_corrected)
    
    df = df_strong.assign(foo=1).merge(df_weak.assign(foo=1), on='foo', suffixes=('_strong', '_weak')).drop('foo', 1)
    df['sum'] = df['sum_strong'] + df['sum_weak']
    df['sum_multiplied'] = df['sum'] * danger_booster
    df = df[df['sum'] <= exp_corrected].sort_values('sum', ascending=False)
    
    output_message = print_output(n_heroes=n_heroes, experience=experience, n_strong=n_strong, n_weak=n_weak, threshold=threshold, insignificance_threshold=insignificance_threshold, danger_booster=danger_booster)
    df = df.head().reset_index(drop=True)
    df['Враги'] = df['combinations_strong'] + df['combinations_weak']
    df['Сумма'] = df['sum_multiplied']
    df = df[['Враги', 'Сумма']]
    print(tabulate(df, headers='keys', tablefmt='psql'))
    return(output_message, df.to_string(index=False))


if __name__=='__main__':
    with open("config/defaults.json") as fp:
        defaults = json.load(fp)
    generate_fight(
        input_handle("experience", "Суммарный опыт", int, defaults),
        input_handle("n_strong", "Число сильных чудовищ", int, defaults),
        input_handle("n_weak", "Число слабых чудовищ", int, defaults),
        input_handle("n_heroes", "Число героев", int, defaults),
        input_handle("insignificance_threshold", "Порог незначительности", float, defaults)
    )
