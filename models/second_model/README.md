# Sugarscape Model

## What the model does and why I chose it

The Sugarscape model is a classic agent-based simulation originally introduced by 
Epstein & Axtell in their book *Growing Artificial Societies*. The core idea is 
simple: agents roam a grid landscape, collect sugar to survive, and die if they run 
out. Despite these simple rules, the model produces complex and realistic emergent 
behaviours — inequality, clustering, and natural selection — none of which are 
explicitly programmed in.

I chose this model as my second project because it was a significant step up from 
the Boltzmann Wealth Model. It required me to work with a discrete grid space, 
manage a separate resource landscape, implement agent decision-making (vision-based 
movement), and track the simulation over time using Mesa's DataCollector. It also 
produces visually interesting results that are easy to interpret and explain.

---

## How the model works

### The Grid
The simulation takes place on a 30x30 discrete grid with `torus=True`, meaning the 
grid wraps around — agents going off one edge reappear on the opposite side. Each 
cell on the grid holds a certain amount of sugar, forming two "sugar hills" — areas 
of high sugar concentration that fade toward the edges.

### The Agents
Each agent has three personal attributes assigned at creation:
- **Wealth (sugar):** Starting sugar, randomly assigned between 5 and 25
- **Metabolism:** How much sugar the agent burns per step (1–4). High metabolism 
  agents need more sugar to survive
- **Vision:** How far the agent can see on the grid to find sugar (1–6). High vision 
  agents can spot richer cells from further away

### Each step, every agent:
1. **Looks around** within its vision range for the richest empty cell
2. **Moves** to that cell
3. **Eats** all the sugar on that cell
4. **Burns** sugar equal to its metabolism
5. **Dies** if its sugar drops to 0 or below

### Sugar regrowth
After every step, each cell regrows sugar at a fixed rate (`sugar_regrow_rate=1`) 
up to its original maximum. This means rich cells near the hill centres keep 
recovering, making them permanently attractive to agents.

---

## Mesa features used

### 1. Discrete Grid Space — `mesa.spaces.SingleGrid`
```python
self.grid = mesa.spaces.SingleGrid(grid_width, grid_height, torus=True)
```
Mesa's `SingleGrid` enforces that only one agent can occupy a cell at a time. 
Agents use `grid.move_agent()`, `grid.place_agent()`, `grid.remove_agent()`, and 
`grid.is_cell_empty()` to navigate the space. The `torus=True` setting wraps the 
grid edges so there are no boundaries.

### 2. Event Scheduling — `shuffle_do`
```python
self.agents.shuffle_do("step")
```
Every model step, agents are activated in a **randomly shuffled order**. This 
prevents any agent from always going first and having an unfair advantage over 
others — a critical fairness mechanism in agent-based simulations.

### 3. Data Collection — `mesa.DataCollector`
```python
self.datacollector = mesa.DataCollector(
    model_reporters={
        "Population": lambda m: len(m.agents),
        "Avg Wealth": lambda m: (
            sum(a.sugar for a in m.agents) / len(m.agents)
            if len(m.agents) > 0 else 0
        ),
    }
)
```
Mesa's built-in `DataCollector` automatically snapshots model-level statistics at 
every step. Here it tracks total population and average agent wealth, which are 
later retrieved as a Pandas DataFrame for visualisation.

### 4. Visualisation — Matplotlib & Seaborn
Three plots are generated after the simulation:
- Population over time
- Average wealth over time  
- Final grid heatmap with agent positions overlaid

---

## Results and analysis

### Graph 1 — Population Over Time

The simulation started with **50 agents** and by step 25 the population had dropped 
sharply to **34 agents**, where it flatlined for the remaining 75 steps.

**What this means:**
The early die-off represents natural selection. Agents with high metabolism and low 
vision couldn't find and collect sugar fast enough to sustain themselves — they 
starved and were removed from the simulation. The agents that survived to step 25 
had a sustainable balance of vision and metabolism, allowing them to keep themselves 
alive indefinitely. The flat line from step 25 to 100 confirms that the surviving 
population reached a **stable equilibrium** — they had claimed rich enough territory 
to survive permanently.

**Key insight:** The 16 agents that died were not unlucky — they were structurally 
disadvantaged by their attributes. This is emergence: no death rule was written 
based on vision or metabolism directly, yet those attributes determined survival.

---

### Graph 2 — Average Wealth Over Time

The average wealth started low (~12 sugar) and rose steadily throughout the 
simulation, reaching ~130 sugar by step 100.

**What this means:**
Two things drive this curve:

1. **Survivor selection:** As weak agents die off, their low sugar holdings stop 
   dragging the average down. Each death raises the average wealth of the remaining 
   population — not because survivors got richer instantly, but because the poorest 
   agents were removed.

2. **Compounding accumulation:** Surviving agents claimed the richest cells near the 
   sugar hill centres. Since sugar regrows every step, these agents collect more 
   sugar than they burn each step — their wealth compounds over time. The longer they 
   survive, the richer they get.

**Key insight:** The curve steepens noticeably around step 25 — exactly when the 
die-off ends. This confirms that the wealth growth is driven by both the removal of 
poor performers and the compounding advantage of survivors sitting on rich cells.

---

### Graph 3 — Final Grid State

The heatmap shows the sugar distribution and agent positions after 100 steps:

- **Dark brown cells** = high sugar concentration (hill centres)
- **Light yellow cells** = low or depleted sugar (edges and corners)
- **Red dots** = surviving agents

**What this shows:**
The two sugar hills are clearly visible as dark diamond-shaped regions. Almost all 
surviving agents are clustered directly on or immediately around the hill centres — 
the richest cells on the grid. The edges and corners are completely empty of agents 
because the sugar there is too low to sustain survival.

Notably, even the dark hill centres still have sugar remaining despite agents sitting 
on them. This is because sugar regrows every step — agents are effectively **farming 
the same rich cells repeatedly**, collecting regrown sugar each step in a sustainable 
loop.

**Key insight:** The spatial clustering was never programmed. No rule told agents to 
cluster at hill centres. It emerged purely from each agent individually following the 
rule: *"move to the richest cell you can see."* When many agents follow this rule 
independently, they all converge on the same rich areas.

---

## What I learned building it

- **How Mesa's grid system works** — the difference between `SingleGrid` and 
  `MultiGrid`, how to place/move/remove agents, and how `torus=True` handles 
  boundary wrapping with the modulo operator
- **How to separate the resource landscape from the agent grid** — the sugar values 
  are stored in a separate numpy array (`grid_sugar`) rather than on the grid cells 
  themselves, which meant I had to keep both in sync manually
- **How DataCollector works in practice** — defining `model_reporters` as lambda 
  functions and pulling the results out as a DataFrame at the end for plotting
- **What emergence actually means** — reading about it and seeing it happen in your 
  own simulation are very different things. The clustering, the die-off, and the 
  wealth inequality were not programmed — they came out of simple rules interacting 
  over time

---

## What was hard, what surprised me, and what I'd do differently

**What was hard:**  
The torus wrapping logic inside `get_best_cell` took me time to understand. Using 
the modulo operator `%` to wrap coordinates felt unintuitive at first — but once I 
visualised it as the grid looping back on itself like a donut, it clicked.

**What surprised me:**  
The speed of the die-off. All 16 deaths happened within the first 25 steps out of 
100. I expected a gradual decline, not a sharp early crash followed by complete 
stability. It shows how quickly natural selection eliminates the unfit when resources 
are scarce and competition is real.

**What I'd do differently:**  
- Add **agent-level data collection** to track individual wealth trajectories — it 
  would be interesting to see which specific agents survived and how their wealth 
  grew compared to those that died
- Introduce **agent reproduction** — when an agent's wealth crosses a threshold, it 
  spawns a child agent. This would allow the population to recover and produce more 
  dynamic population curves
- Experiment with different `sugar_regrow_rate` values to see how resource scarcity 
  affects the equilibrium population size
