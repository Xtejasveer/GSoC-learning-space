## Installing dependancies

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import mesa

## First we are creating a class for how an agent would look and it's wealth

class MoneyAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, model):
        super().__init__(model)

        # Create the agent's variable and set the initial values.
        self.wealth = 1
    # def say_hi(self):
    #     #This is the function that will be called every time the agent gets selected randomly by the model
    #     print(f'Hi, I am an agent, you can call me {self.unique_id}.')
    def say_wealth(self):
        #This function will print the wealth for each agent
        print(f"Hi, I am an agent and my wealth is {self.wealth}")

    def exchange(self):
        ## This function defines the money being exchanged
        if self.wealth>0:
            other_agent = self.random.choice(self.model.agents)
            if other_agent is not None:
                other_agent.wealth +=1
                self.wealth -=1

## Now we are building a model around this 
class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, n=10, seed=None):
        super().__init__(seed=seed) ## This line of code runs the mesa.Model's(Parent) __init__ first and then money model's own setup is ran
        self.num_agents = n
        # Create agents
        MoneyAgent.create_agents(model=self, n=n)
    
    def step(self):
        """Advance the model one by one"""
        #This function rorders the list of agents and iterated through them while calling the function we defined earlier

        self.agents.shuffle_do("exchange")
        self.agents.shuffle_do("say_wealth")


# starter_model = MoneyModel(12)
# starter_model.step()

model = MoneyModel(10)
for _ in range(30):
    model.step()

agent_wealth = [a.wealth for a in model.agents]

g= sns.histplot(agent_wealth, discrete = True)
g.set(
    title = "Wealth Distribution",
    xlabel = 'Wealth',
    ylabel = 'Number of agents'
);
plt.show()