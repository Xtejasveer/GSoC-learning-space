## Installing dependencies

import mesa
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

class SugarAgent(mesa.Agent):
    """ An agent that moves towards sugar and consumes it to survive."""

    def __init__(self, model, metabolism, vision):
        super().__init__(model)
        self.metabolism = metabolism ## Amount of sugar they burn per step
        self.vision = vision ## How far they can see on the grid
        self.sugar = self.random.randint(5,25) ## Starting wealth

    #where to move to get the most sugar
    def get_best_cell(self):
        x,y = self.pos
        best_pos = self.pos
        best_sugar = self.model.grid_sugar[x][y]

        for dx in range(-self.vision, self.vision+1):
            for dy in range(-self.vision, self.vision+1):
                nx, ny = (x+dx)%self.model.grid_width, (y+dy)%self.model.grid_height
                cell_sugar = self.model.grid_sugar[nx][ny]
                if cell_sugar > best_sugar and self.model.grid.is_cell_empty((nx,ny)):
                    best_sugar = cell_sugar
                    best_pos = (nx,ny)
        return best_pos

    def move(self):
        best_pos = self.get_best_cell()
        if best_pos != self.pos:
            self.model.grid.move_agent(self, best_pos)
    
    def eat(self):
        x, y = self.pos
        self.sugar += self.model.grid_sugar[x][y]
        self.model.grid_sugar[x][y] = 0
        self.sugar -= self.metabolism

    def step(self):
        self.move()
        self.eat()
        if self.sugar <=0:
            self.model.grid.remove_agent(self)
            self.remove()


class SugarscrapeModel(mesa.Model):
    """
    Sugarscrape model where agents move in a grid and collect sugar to survive, agents with poor metabolism 
    or low vision die.
    """

    def __init__(self, n =50, grid_width =30, grid_height =30, sugar_regrow_rate=1, max_sugar=4, seed= None):
        super().__init__(seed=seed)

        self.grid_width = grid_width
        self.grid_height = grid_height
        self.sugar_regrow_rate = sugar_regrow_rate
        self.max_sugar = max_sugar

        self.grid = mesa.space.SingleGrid(grid_width, grid_height, torus=True)

        self.grid_sugar = np.zeros((grid_width, grid_height))
        self.max_sugar_grid = np.zeros((grid_width, grid_height))
        self.initialize_sugar()

        #Data collector
        self.datacollector = mesa.DataCollector(
            model_reporters ={
                'Population' : lambda m : len(m.agents),
                'Avg Wealth' : lambda m : (
                    sum(a.sugar for a in m.agents) /len(m.agents)
                    if len(m.agents) > 0 else 0
                ),
            }
        )
        
        ## Create agents with random metabolism and vision
        SugarAgent.create_agents(
            model = self,
            n = n,
            metabolism = self.random.randint(1,4),
            vision  = self.random.randint(1,6)
        )

        empty_cells = list(self.grid.empties)
        self.random.shuffle(empty_cells)
        for agent, cell in zip(self.agents, empty_cells[:n]):
            self.grid.place_agent(agent, cell)
    
    def initialize_sugar(self):
        """ Create sugar hills"""
        cx1, cy1  = self.grid_width//4 , self.grid_height//4
        cx2, cy2  = 3*self.grid_width//4 , 3* self.grid_height//4

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                d1 = abs(x-cx1) + abs(y-cy1)
                d2 = abs(x-cx2) + abs(y-cy2)
                sugar = max(0, self.max_sugar - min(d1,d2) //3)
                self.grid_sugar[x][y] = sugar
                self.max_sugar_grid[x][y] = sugar
    def regrow_sugar(self):
        """Sugar grows back each step up to its max value."""
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.grid_sugar[x][y] = min(
                    self.grid_sugar[x][y] + self.sugar_regrow_rate,
                    self.max_sugar_grid[x][y]
                )
    def step(self):
        """At each step the model - regrow sugar, shuffle agents, collect data"""
        self.regrow_sugar()
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)

model = SugarscrapeModel(n=50, seed=42)

for _ in range(100):
    model.step()


df = model.datacollector.get_model_vars_dataframe()

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Sugarscape Simulation", fontsize=14, fontweight="bold")

# Plot 1 — Population over time
axes[0].plot(df["Population"], color="steelblue", linewidth=2)
axes[0].set_title("Population Over Time")
axes[0].set_xlabel("Step")
axes[0].set_ylabel("Number of Agents")
axes[0].grid(True, alpha=0.3)

# Plot 2 — Average wealth over time
axes[1].plot(df["Avg Wealth"], color="goldenrod", linewidth=2)
axes[1].set_title("Average Wealth Over Time")
axes[1].set_xlabel("Step")
axes[1].set_ylabel("Avg Sugar")
axes[1].grid(True, alpha=0.3)

# Plot 3 — Final sugar grid heatmap with agent positions overlaid
sugar_display = model.grid_sugar.T
axes[2].imshow(sugar_display, cmap="YlOrBr", origin="lower", interpolation="nearest")

agent_positions = [a.pos for a in model.agents]
if agent_positions:
    ax_vals, ay_vals = zip(*agent_positions)
    axes[2].scatter(ax_vals, ay_vals, c="red", s=15, label="Agents")

axes[2].set_title("Final Grid State")
axes[2].set_xlabel("X")
axes[2].set_ylabel("Y")
axes[2].legend(loc="upper right", fontsize=8)

plt.tight_layout()
plt.show()