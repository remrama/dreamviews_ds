"""
Visualize DreamViews activity over time.
The main plot is for post frequency but user frequency is on top too.

The optional command line arguments are just for changes to make presentation plots (can ignore).

IMPORTS
=======
    - posts, derivatives/dreamviews-posts.tsv
EXPORTS
=======
    - visualization,              results/describe-timecourse.png
    - total post and user counts, results/describe-totalcounts.tsv
"""
import os
import argparse
import pandas as pd
import config as c

import seaborn as sea
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
c.load_matplotlib_settings()

parser = argparse.ArgumentParser()
parser.add_argument("--white", action="store_true", help="To ignore labels and just plot all data in white")
parser.add_argument("--restrict", action="store_true", help="To restrict data to lucid and non-lucid labels")
args = parser.parse_args()

WHITE = args.white
RESTRICT = args.restrict


################################ I/O

export_fname = os.path.join(c.DATA_DIR, "results", "describe-timecourse.png")
export_fname_totals = os.path.join(c.DATA_DIR, "results", "describe-totalcounts.tsv")
if WHITE:
    export_fname = export_fname.replace(".png", "_WHITE.png")
if RESTRICT:
    export_fname = export_fname.replace(".png", "_RESTRICT.png")

df = c.load_dreamviews_posts()

# drop data if desired
if RESTRICT:
    df = df[ df["lucidity"].str.contains("lucid") ]

### generate a dataframe of user counts by month
### that accounts for novel/repeat users
df["year"] = df["timestamp"].dt.year
df["month"] = df["timestamp"].dt.month

monthly_users = df.drop_duplicates(ignore_index=True,
        subset=["user_id","year","month"]
    ).copy().sort_values("timestamp")
# find novel users
monthly_users["novel"] = monthly_users.user_id.duplicated(
    keep="first").map({True: "repeat-user", False: "novel-user"})



################################ Plotting

############ first specify a lot of parameters for plotting

if RESTRICT:
    LUCIDITY_ORDER = ["nonlucid", "lucid"]
else:
    LUCIDITY_ORDER = ["unspecified", "ambiguous", "nonlucid", "lucid"]
USER_ORDER = ["repeat-user", "novel-user"]

LEGEND_LABELS = {
    "unspecified" : "unspecified",
    "ambiguous"   : "ambiguous (both)",
    "nonlucid"    : "non-lucid",
    "lucid"       : "lucid",
    "novel-user"  : "novel",
    "repeat-user" : "repeat",
}

RIGHT_AX_COLOR = "gray"
GRID_COLOR = "gainsboro"

# to keep the grid useful for both left/right axes,
# pick a single multiplication factor to use for lots of stuff
RIGHT_AX_MULT_FACTOR = 30

MINOR_TICK_DIV_FACTOR = 5 # n minor ticks per major
TICK_WIDTH = dict(major=1, minor=.3)

# monthly is for left axis, cumulative is for right axis
POST_YMAX_MONTHLY = 2000
USER_YMAX_MONTHLY = 500

post_ymax_cumulative = POST_YMAX_MONTHLY * RIGHT_AX_MULT_FACTOR
user_ymax_cumulative = USER_YMAX_MONTHLY * RIGHT_AX_MULT_FACTOR

post_ymax = dict(monthly=POST_YMAX_MONTHLY, cumulative=POST_YMAX_MONTHLY*RIGHT_AX_MULT_FACTOR)
user_ymax = dict(monthly=USER_YMAX_MONTHLY, cumulative=USER_YMAX_MONTHLY*RIGHT_AX_MULT_FACTOR)

major_tick_loc_left = USER_YMAX_MONTHLY
major_tick_loc_right = major_tick_loc_left * RIGHT_AX_MULT_FACTOR
minor_tick_loc_left = major_tick_loc_left // MINOR_TICK_DIV_FACTOR
minor_tick_loc_right = major_tick_loc_right // MINOR_TICK_DIV_FACTOR

XMIN = pd.to_datetime("2010-01-01")
XMAX = pd.to_datetime("2021-01-01")

n_years = (XMAX-XMIN).days // 365
n_bins = n_years * 12 # to get 1 bin/tick per month
binrange = (mdates.date2num(XMIN), mdates.date2num(XMAX))

PLOT_ARGS = { # that go to ALL 4 plots
    "x"          : "timestamp",
    "alpha"      : 1,
    "linewidth"  : .5,
    "multiple"   : "stack",
    "legend"     : False,
    "bins"       : n_bins,
    "binrange"   : binrange,
    "palette"   : c.COLORS,
}

MONTHLY_PLOT_ARGS = {
    "edgecolor"  : "black",
    "element"    : "bars",
    "fill"       : True,
    "cumulative" : False,
}

CUMULATIVE_PLOT_ARGS = {
    "element"    : "step",
    "fill"       : False,
    "cumulative" : True,
}

LEGEND_ARGS = {
    "borderaxespad" : 0,
    "frameon"       : False,
    "labelspacing"  : .2, # vertical space between entries
    "handletextpad" : .2, # space between legend markers and labels
}

GRIDSPEC_KWS = {
    "height_ratios" : [USER_YMAX_MONTHLY, POST_YMAX_MONTHLY],
    # "hspace" : .05,
}

if WHITE:
    post_plot_args = {"color": "white"}
    user_plot_args = {"color": "white"}
else:
    post_plot_args = { # for bottom axis
        "hue"       : "lucidity",
        "hue_order" : LUCIDITY_ORDER,
    }
    user_plot_args = { # for top axis
        "hue"       : "novel",
        "hue_order" : USER_ORDER,
    }


############ now draw


# open figure and create twin axes
_, axes = plt.subplots(2, 1,
    figsize=(6.5, 2.5),
    sharex=True, sharey=False,
    constrained_layout=True,
    gridspec_kw=GRIDSPEC_KWS)

ax2a, ax1a = axes
ax1b = ax1a.twinx()
ax2b = ax2a.twinx()

ax1a.set_xlim(XMIN, XMAX)

# draw the four plots (top/bottom and left/right axes)
sea.histplot(ax=ax1a, data=df, **post_plot_args, **MONTHLY_PLOT_ARGS, **PLOT_ARGS)
sea.histplot(ax=ax1b, data=df, **post_plot_args, **CUMULATIVE_PLOT_ARGS, **PLOT_ARGS)
sea.histplot(ax=ax2a, data=monthly_users, **user_plot_args, **MONTHLY_PLOT_ARGS, **PLOT_ARGS)
sea.histplot(ax=ax2b, data=monthly_users, **user_plot_args, **CUMULATIVE_PLOT_ARGS, **PLOT_ARGS)
if WHITE:
    ax1b.lines[0].set(color="black", alpha=1)
    ax2b.lines[0].set(color="black", alpha=1)

# legends
if not WHITE:

    ###### bottom legend
    ax1_handles = [ plt.matplotlib.patches.Patch(edgecolor="none",
            facecolor=c.COLORS[cond], label=LEGEND_LABELS[cond])
        for cond in LUCIDITY_ORDER ]
    ax1_legend = ax1b.legend(handles=ax1_handles,
        bbox_to_anchor=(.6, .55), loc="lower left",
        **LEGEND_ARGS)
    # ax1_legend.get_frame().set_linewidth(0)

    ###### top legend
    ax2_handles = [ plt.matplotlib.patches.Patch(edgecolor="none",
            facecolor=c.COLORS[cond], label=LEGEND_LABELS[cond])
        for cond in USER_ORDER ]
    ax2_legend = ax2b.legend(handles=ax2_handles,
        bbox_to_anchor=(.6, .98), loc="upper left",
        **LEGEND_ARGS)
    # ax2_legend.get_frame().set_linewidth(0)

###### aesthetics on bottom axis
ax1a.set_xlabel("Year")
ax1a.set_ylabel(r"$n$ posts, monthly")
ax1a.set_ybound(upper=POST_YMAX_MONTHLY)
ax1b.set_ybound(upper=post_ymax_cumulative)

###### aesthetics on top axis
ax2a.set_ylabel(r"$n$" + " users,\nmonthly")
ax2a.set_ybound(upper=USER_YMAX_MONTHLY)
ax2b.set_ybound(upper=user_ymax_cumulative)
ax2a.xaxis.set(major_locator=mdates.YearLocator(),
               minor_locator=mdates.MonthLocator(),
               major_formatter=mdates.DateFormatter("%Y"))

###### aesthetics consistent on top and bottom
ax1b.set_ylabel("cumulative", rotation=270, va="bottom", color=RIGHT_AX_COLOR)
ax2b.set_ylabel("cumulative", rotation=270, va="bottom", color=RIGHT_AX_COLOR)
ax1b.spines["right"].set_color(RIGHT_AX_COLOR)
ax2b.spines["right"].set_color(RIGHT_AX_COLOR)
ax1a.tick_params(which="both", axis="y", direction="in")
ax2a.tick_params(which="both", axis="y", direction="in")
ax1b.tick_params(which="both", axis="y", direction="in", colors=RIGHT_AX_COLOR)
ax2b.tick_params(which="both", axis="y", direction="in", colors=RIGHT_AX_COLOR)
ax1a.set_axisbelow(True)
ax2a.set_axisbelow(True)
ax1a.yaxis.grid(which="major", color=GRID_COLOR, linewidth=TICK_WIDTH["major"])
ax2a.yaxis.grid(which="major", color=GRID_COLOR, linewidth=TICK_WIDTH["major"])
ax1a.yaxis.grid(which="minor", color=GRID_COLOR, linewidth=TICK_WIDTH["minor"])
ax2a.yaxis.grid(which="minor", color=GRID_COLOR, linewidth=TICK_WIDTH["minor"])
ax1a.yaxis.set(major_locator=plt.MultipleLocator(major_tick_loc_left),
               minor_locator=plt.MultipleLocator(minor_tick_loc_left))
ax2a.yaxis.set(major_locator=plt.MultipleLocator(major_tick_loc_left),
               minor_locator=plt.MultipleLocator(minor_tick_loc_left))
ax1b.yaxis.set(major_locator=plt.MultipleLocator(major_tick_loc_right),
               minor_locator=plt.MultipleLocator(minor_tick_loc_right))
ax2b.yaxis.set(major_locator=plt.MultipleLocator(major_tick_loc_right),
               minor_locator=plt.MultipleLocator(minor_tick_loc_right))

##### draw total counts on the plot
n_total_posts = df.shape[0]
n_total_users = df["user_id"].nunique()
# label_counts = df["lucidity"].value_counts().rename_axis("n_posts")
# n_users_per_label = df.groupby("lucidity").user_id.nunique("")
counts_txt = fr"$n_{{total}}={n_total_posts}$"
users_txt = fr"$n_{{total}}={n_total_users}$"
ax1a.text(.3, .9, counts_txt, transform=ax1a.transAxes, ha="left", va="top")
ax2a.text(.3, .9, users_txt, transform=ax2a.transAxes, ha="left", va="top")

# export
ser = pd.Series([n_total_posts, n_total_users],
    index=pd.Index(["posts", "users"], name="total"), name="count")
ser.to_csv(export_fname_totals, index=True, sep="\t")

plt.savefig(export_fname)
c.save_hires_figs(export_fname)
plt.close()