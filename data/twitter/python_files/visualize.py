import datetime

import matplotlib.pyplot as plt

plt.ion()
_, ax = plt.subplots(figsize=(10, 5))
ax.set_xlabel("UTC Time", fontsize=12)
ax.set_ylabel("Sentiment score", fontsize=12)
ax.set_title("Twitter", fontsize=14)

n_iters = 0  # keep track of the number of iterations / data points

while True:
    count = 0  # keep track the number of iterations in the current while loop
    # initialize empty lists to store datetime and scores
    dts = []
    scores = []
    with open("../data/twitter_sentiment_scores.txt", 'r') as f:
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
    colors = 'deepskyblue' if scores[-1] < -0.05 else 'deeppink'  # color based on sentiment score
    ax.plot(dts, scores, color='grey', alpha=0.8, zorder=10)
    ax.scatter(dts, scores, marker='o', color=colors, alpha=0.8, zorder=11)
    plt.draw()
    plt.pause(10)  # wait 10s for data to be updated
