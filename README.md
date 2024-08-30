# Galaga_RL

The model used to play galaga was created using the stable-retro continutation of OpenAI's gym system. Stable-retro allows us to explain reinforcement learning on games that aren't just available on Atari. In order to use Galaga, a ROM was needed to be downloaded and imported into stable retro along with a folder containing information that allows stable retro to analyze the NES game.

The folder includes:
- 1Player.Level1.state tells stable retro what the first frame of the game is (i.e. the start)
- data.json indicates where to find the variables included in the game
- scenario.json notes the reward function and done condition.
- metadata.json creates a default starting state
- rom.nes and rom.sha help with importing the ROM and allowing stable retro to access it.

### Galaga Performance
