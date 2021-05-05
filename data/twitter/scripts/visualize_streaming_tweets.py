import datetime

import matplotlib.pyplot as plt

category = 'cryptocurrency'
keywords = 'bitcoin,coinbase'
# category = 'energy'
# keywords = 'oil,gas,energy'
# category = 'test_for_fun'
# keywords = 'Bill Gates'

plt.ion()
_, ax = plt.subplots(figsize=(10, 5))
ax.set_xlabel("US/Eastern Time", fontsize=12)
ax.set_ylabel("Sentiment score", fontsize=12)
ax.set_title("Twitter (" + keywords + ")", fontsize=14)

n_iters = 0  # keep track of the number of iterations / data points

while True:
    count = 0  # keep track the number of iterations in the current while loop
    # initialize empty lists to store datetime and scores
    dts = []
    scores = []
    with open("../data/streaming/twitter_sentiment_scores_" + category + ".txt", 'r') as f:
        # read line by line
        lines = f.read().split('\n')

        # iterate over lines starting from 0 or the previous iteration
        start = n_iters if n_iters == 0 else n_iters - 1
        for line in lines[start:]:
            if line:
                dt, score = line.split('\t')
                dts.append(dt)
                scores.append(float(score))
                count += 1
    dts = [datetime.datetime.strptime(dt, "%Y%m%d%H%M%S") for dt in dts]
    count -= 1 if start == n_iters - 1 else 0  # subtract 1 from count if starting from the previous iteration
    n_iters += count
    print("Number of data points:", n_iters)
    # color based on sentiment score
    colors = []
    for score in scores:
        if score >= 0.05:  # positive
            colors.append('forestgreen')
        elif score <= -0.05:  # negative
            colors.append('deeppink')
        else:  # neutral
            colors.append('deepskyblue')
    ax.plot(dts, scores, color='grey', zorder=10)
    ax.scatter(dts, scores, marker='o', color=colors, zorder=11)
    plt.draw()
    plt.pause(10)  # wait 10s for data to be updated
