import Box2D  # The main library
# Box2D.b2 maps Box2D.b2Vec2 to vec2 (and so on)

from Box2D.b2 import (world, polygonShape, circleShape, staticBody, dynamicBody, AABB)

import random
import math

class TowerWorld(object):
    def __init__(self):
        self.world = world(gravity=(0, -10), doSleep=True)
        self.ground_body = self.world.CreateStaticBody(
            position=(0, 0),
            shapes=polygonShape(box=(50, 1)),
            userData = {"color": (255, 255, 255, 255) }
        )

        self.blocks = []

        w = 2.5
        h = 0.4
        self.blockSize = {True: (w,h),
                          False: (h,w)}
        self.blockOffset = {True: 0.0,
                            False: 0.}
        # self.H = 3.
        # self.W = 0.5
        self.dt = 1./60
        self.locationNoise = 0.0

    def lowestLegalHeight(self, x, dx, dy):
        lowest = dy + 0.5 # the floor

        x1 = x - dx
        x2 = x + dx

        for b in self.blocks:
            # Fuck you box2d
            assert len(b.fixtures) == 1
            xs = [ (b.transform * v)[0]
                   for v in b.fixtures[0].shape.vertices ]
            ys = [ (b.transform * v)[1]
                   for v in b.fixtures[0].shape.vertices ]
            x1_ = min(xs)
            x2_ = max(xs)
            y1_ = min(ys)
            y2_ = max(ys)

            if x1_ > x2 or x1 > x2_: continue

            lowest = max(lowest, y2_ + dy)

        return lowest

            

    def placeBlock(self, x, orientation):
        x += 11

        x += random.random()*self.locationNoise - self.locationNoise/2
        
        dx,dy = self.blockSize[orientation]
        x += self.blockOffset[orientation]
        dx = dx/2
        dy = dy/2

        safetyMargin = 0.1
        y = self.lowestLegalHeight(x, dx, dy) + safetyMargin
        
        body = self.world.CreateDynamicBody(position=(x, y),
                                            angle=0,
                                            userData = {"color":
                                                        tuple(random.random()*128+127 for _ in range(4) ),
                                                        "p0": (x,y)})
        box = body.CreatePolygonFixture(box=(dx, dy), density=1, friction=0.9)
        self.blocks.append(body)

    def step(self, dt):
        self.world.Step(dt, 10, 10)

    def unmoving(self):
        return all( abs(b.linearVelocity[0]) < 0.05 and abs(b.linearVelocity[1]) < 0.05
                    for b in self.blocks ) 

    def height(self):
        if self.blocks == []: return 0
        return max( (b.transform * v)[1]
                 for b in self.blocks
                 for v in b.fixtures[0].shape.vertices )

    def length(self):
        if self.blocks == []: return 0
        xs = [ (b.transform * v)[0]
               for b in self.blocks
               for v in b.fixtures[0].shape.vertices ]
        return max(xs) - min(xs)

    def impartImpulses(self, p):
        for b in self.blocks:
            b.ApplyLinearImpulse([random.random()*p - p/2,
                                  random.random()*p],
                                 b.worldCenter,
                                 True)
            b.ApplyAngularImpulse(random.random()*p - p/2,
                          True)

    def stepUntilStable(self):
        for _ in range(50): self.step(self.dt)
        for _ in range(100000):
            self.step(self.dt)
            if self.unmoving(): break

    def blocksSignificantlyMoved(self, threshold):
        for b in self.blocks:
            p = (b.worldCenter[0], b.worldCenter[1])
            p0 = b.userData["p0"]
            d = (p[0] - p0[0],
                 p[1] - p0[1])
            r = d[0]**2 + d[1]**2
            if r > threshold: return True
        return False
        
    def executePlan(self, plan):
        initialHeight = float('-inf')
        badPlan = False
        for p in plan:
            self.placeBlock(*p)
            self.stepUntilStable()
            newHeight = self.height()
            if newHeight < initialHeight - 0.1: badPlan = True
            initialHeight = newHeight

            if self.blocksSignificantlyMoved(1):
                badPlan = True
                break
        return not badPlan
    
    def clearWorld(self):
        for b in self.blocks:
            self.world.DestroyBody(b)
        self.blocks = []

    def sampleStability(self, plan, perturbation, N = 5):
        hs = []
        wasStable = []
        for _ in range(N):
            planSucceeds = self.executePlan(plan)
            if planSucceeds:
                initialHeight = self.height()
                hs.append(initialHeight)
                self.impartImpulses(perturbation)
                self.stepUntilStable()
                wasStable.append(True #(not self.blocksSignificantlyMoved(1)) \
                                 and (self.height() > initialHeight - 0.1))
            else:
                hs.append(0.)
                wasStable.append(False)

            # reset the world
            self.clearWorld()
        h = sum(hs)/N
        return h, sum(wasStable)/float(len(wasStable))
    
            
