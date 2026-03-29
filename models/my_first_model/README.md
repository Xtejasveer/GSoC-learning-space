# Boltzmann Wealth Model

## What the model does and why I chose it

This is an implementation of the Boltzmann Wealth Model — one of the simplest 
agent-based models in economics. Each agent starts with a wealth of 1 and at every 
step, randomly gives 1 unit of wealth to another agent (as long as they have wealth 
to give). Over many steps, this completely random exchange process produces a highly 
unequal wealth distribution — which mirrors patterns seen in real economies.

I chose this model because it was recommended as a starting point for Mesa, and it 
turned out to be a great choice. The rules are simple enough to understand in 5 
minutes, but the emergent behaviour (inequality from randomness alone) is genuinely 
surprising and gives you something real to think about.

## Mesa features used

- **`mesa.Agent`** — base class for defining agent behaviour (`exchange`, `say_wealth`)
- **`mesa.Model`** — base class for the model, manages agents and steps
- **`MoneyAgent.create_agents()`** — Mesa's built-in way to batch-create agents and 
  automatically register them with the model
- **`self.agents.shuffle_do()`** — randomly reorders agents and calls a method on 
  each one, ensuring no agent always goes first
- **`self.random`** — Mesa's seeded random number generator, used to pick a random 
  other agent during exchange

## What I learned building it

- How Mesa separates agent logic from model logic — the agent handles its own 
  behaviour (`exchange`), and the model just orchestrates when that happens (`step`)
- How `super().__init__()` works in practice — both `MoneyAgent` and `MoneyModel` 
  inherit from Mesa base classes, and calling `super().__init__()` ensures Mesa's 
  own setup runs before the custom code
- How `shuffle_do` prevents order bias — if agents always acted in the same order, 
  the first agent would always have an advantage. Shuffling each step makes the 
  simulation fair
- How to visualise results with seaborn — using `histplot` with `discrete=True` to 
  show wealth distribution after running the model for 30 steps

## What was hard, what surprised me, and what I'd do differently

**What was hard:** Understanding why `create_agents()` is preferred over manually 
instantiating agents in a loop. It's not obvious at first, but it cleanly handles 
agent registration with the model behind the scenes.

**What surprised me:** The wealth distribution that emerges is strikingly unequal 
even though every agent starts with the same wealth and the exchange is completely 
random. There is no "rich agent" programmed in — inequality just emerges. That was 
a genuinely interesting result.

**What I'd do differently:** I'd add Mesa's built-in `DataCollector` to track wealth 
distribution over time at each step, rather than only looking at the final state. 
That would make it possible to visualise *how* the inequality develops, not just 
where it ends up.