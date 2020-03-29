import gym
from app_class import *

if __name__ == '__main__':
    #app = App()
    # app.run()

    env = App()
    env.reset()

    for i_episode in range(20):
        # observation = env.reset()
        for t in range(100):
            # print(observation)
            action = env.action_space.sample()
            observation, reward, done = env.step(action)
            if done:
                print("Episode finished after {} timesteps".format(t+1))
                break
    env.close()
