import sys
import pygame
import numpy
import random
import time as t
from config import *


class Game():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris!")
        self.time = pygame.time
        self.clock = pygame.time.Clock()

        self.base_architecture = numpy.array(BASE_ARCHITECTURE)
        self.current_architecture = self.base_architecture.copy()
        self.current_block_architectures = random.choice([T_SHAPES_ARCHITECTURES, S_SHAPES_ARCHITECTURES, Z_SHAPES_ARCHITECTURES, J_SHAPES_ARCHITECTURES, L_SHAPES_ARCHITECTURES, I_SHAPES_ARCHITECTURES, O_SHAPES_ARCHITECTURES])
        self.current_block_architecture_index = 0
        self.current_block_architecture = numpy.array(self.current_block_architectures[self.current_block_architecture_index])
        self.block_x_position_increment = 0
        self.block_y_position_increment = 0
        self.adjustNewBlockPos()

        self.next_block_architectures = random.choice([T_SHAPES_ARCHITECTURES, S_SHAPES_ARCHITECTURES, Z_SHAPES_ARCHITECTURES, J_SHAPES_ARCHITECTURES, L_SHAPES_ARCHITECTURES, I_SHAPES_ARCHITECTURES, O_SHAPES_ARCHITECTURES])
        self.next_block_architecture_index = 0
        self.next_block_architecture = numpy.array(self.next_block_architectures[self.next_block_architecture_index])

        self.base_color_architecture = self.base_architecture.copy()
        self.current_color_architecture = self.base_architecture.copy()
        self.available_block_colors = [RED, GREEN, BLUE, YELLOW]
        self.available_block_light_colors = [LIGHTRED, LIGHTGREEN, LIGHTBLUE, LIGHTYELLOW]
        self.current_block_color_index = random.randint(0, len(self.available_block_colors))

        self.game_score = 0.0
        self.game_level_min = 1
        self.game_level_max = 10
        self.game_level = 1

        self.last_block_fall_time = self.time.get_ticks()
        self.block_fall_delay = 1000 / self.game_level

        self.last_scheduler_update_time = self.time.get_ticks()
        self.scheduler_update_delay = 1000

    def loadIninitalScene(self):
        self.drawText("Tetris!", 100, (SCREEN_WIDTH / 2, 150), WHITE)
        self.drawText("Left / Right / Down Arrow keys to move blocks", 50, (SCREEN_WIDTH / 2, 300), WHITE)
        self.drawText("Up arrow key to rotate blocks", 50, (SCREEN_WIDTH / 2, 400), WHITE)
        self.drawText("Space key to drop blocks immediately", 50, (SCREEN_WIDTH / 2, 500), WHITE)
        self.drawText("Z and X key to change game level", 50, (SCREEN_WIDTH / 2, 600), WHITE)

        self.drawText("Click s to start!", 50, (SCREEN_WIDTH / 2, 800), WHITE)
        pygame.display.flip()

        #self.drawText("Score: ", 50, (SCREEN_WIDTH / 2 + self.base_architecture.shape[1] * BOX_SIZE / 2, 50), BLUE)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        return True


    def run(self):
        while True:
            self.clock.tick(FPS)
            self.fallBlockStepByStep()
            self.event()
            self.updateCurrentArchitecture()
            self.updateCurrentColorArchitecture()
            self.draw()
            if self.checkGameOverCondition():
                if self.loadGameOverScene():
                    self.restartGame()
            #self.updateScheduler()

    def fallBlockStepByStep(self):
        now = self.time.get_ticks()
        if now - self.last_block_fall_time > self.block_fall_delay:
            self.last_block_fall_time = now
            if self.canBlockMoveDownward():
                self.moveBlockDownward()
            else:
                rowsToDelete = self.checkRowsDeletion()
                if len(rowsToDelete) > 0:
                    self.highlightRowsToBeDeleted(rowsToDelete)
                    self.deleteRows(rowsToDelete)
                    self.game_score += (len(rowsToDelete) + self.game_level) * 10
                self.spawnNewBlock()

    def checkRowsDeletion(self):
        rowsToDelete = []
        for y in range(self.current_architecture.shape[0]):
            if numpy.sum(self.current_architecture[y][:]) == 210:
                rowsToDelete.append(y)
        return rowsToDelete

    def highlightRowsToBeDeleted(self, rowsToDelete):
        highlightRepeat = 3
        currentHighlightedColor = [WHITE, RED][0]
        for y in range(self.current_architecture.shape[0]):
            if y in rowsToDelete:
                for x in range(self.current_architecture.shape[1]):
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH / 2 - self.base_architecture.shape[1] * BOX_SIZE / 2, y * BOX_SIZE), BOX_SIZE, BOX_SIZE, WHITE)
                    pygame.display.flip()
                for x in range(self.current_architecture.shape[1]):
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH / 2 - self.base_architecture.shape[1] * BOX_SIZE / 2, y * BOX_SIZE), BOX_SIZE, BOX_SIZE, RED)
                    pygame.display.flip()
                for x in range(self.current_architecture.shape[1]):
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH / 2 - self.base_architecture.shape[1] * BOX_SIZE / 2, y * BOX_SIZE), BOX_SIZE, BOX_SIZE, WHITE)
                    pygame.display.flip()
                t.sleep(0.1)


    def deleteRows(self, rowsToDelete):
        self.current_architecture = numpy.delete(self.current_architecture, rowsToDelete, axis = 0)
        for row in rowsToDelete:
            self.current_architecture = numpy.insert(self.current_architecture, 1, [100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100], axis = 0)

    def spawnNewBlock(self):
        self.base_architecture = self.current_architecture.copy()

        self.current_block_architectures = self.next_block_architectures.copy()
        self.current_block_architecture_index = 0
        self.current_block_architecture = numpy.array(self.next_block_architectures[self.current_block_architecture_index])
        self.block_x_position_increment = 0
        self.block_y_position_increment = 0
        self.adjustNewBlockPos()

        self.next_block_architectures = random.choice([T_SHAPES_ARCHITECTURES, S_SHAPES_ARCHITECTURES, Z_SHAPES_ARCHITECTURES, J_SHAPES_ARCHITECTURES, L_SHAPES_ARCHITECTURES, I_SHAPES_ARCHITECTURES, O_SHAPES_ARCHITECTURES])
        self.next_block_architecture_index = 0
        self.next_block_architecture = numpy.array(self.next_block_architectures[self.next_block_architecture_index])

        self.base_color_architecture = self.current_color_architecture.copy()
        self.current_block_color_index = random.randint(0, len(self.available_block_colors))

    def adjustNewBlockPos(self):
        repeat = 4
        for x in range(repeat):
            if self.canBlockMoveRightward():
                self.moveBlockRightward()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.dropBlock()
                elif event.key == pygame.K_z:
                    self.gameLevelUp()
                elif event.key == pygame.K_x:
                    self.gameLevelDown()
                elif event.key == pygame.K_RIGHT:
                    if self.canBlockMoveRightward():
                        self.moveBlockRightward()
                elif event.key == pygame.K_LEFT:
                    if self.canBlockMoveLeftward():
                        self.moveBlockLeftward()
                elif event.key == pygame.K_UP:
                    if self.canBlockRotate():
                        self.rotateBlock()
                elif event.key == pygame.K_DOWN:
                    if self.canBlockMoveDownward():
                        self.moveBlockDownward()

    def dropBlock(self):
        while self.canBlockMoveDownward():
            self.moveBlockDownward()

    def gameLevelUp(self):
        if self.game_level + 1 <= self.game_level_max:
            self.game_level += 1
        self.block_fall_delay = 1000 / self.game_level


    def gameLevelDown(self):
        if self.game_level - 1 >= self.game_level_min:
            self.game_level -= 1
        self.block_fall_delay = 1000 / self.game_level

    def canBlockMoveRightward(self):
        canMove = True
        temporal_current_block_architecture = []
        for row in self.current_block_architecture:
            temporal_current_block_architecture.append(numpy.roll(row, 1))
        temporal_current_block_architecture = numpy.array(temporal_current_block_architecture)

        temporal_current_architecture = self.base_architecture.copy()
        for y in range(temporal_current_block_architecture.shape[0]):
            for x in range(temporal_current_block_architecture.shape[1]):
                temporal_current_architecture[y + 1][x + 1] += temporal_current_block_architecture[y][x]
                if temporal_current_architecture[y + 1][x + 1] == 2:
                    canMove = False
                    return canMove
        for y in range(self.current_block_architecture.shape[0]):
            if self.current_block_architecture[y][self.current_block_architecture.shape[1] - 1] == 1:
                canMove = False
                return canMove
        return canMove

    def moveBlockRightward(self):
        updated_current_block_architecture = []
        for row in self.current_block_architecture:
            updated_current_block_architecture.append(numpy.roll(row, 1))
        self.block_x_position_increment += 1
        self.current_block_architecture = numpy.array(updated_current_block_architecture).copy()

    def canBlockMoveLeftward(self):
        canMove = True
        temporal_current_block_architecture = []
        for row in self.current_block_architecture:
            temporal_current_block_architecture.append(numpy.roll(row, -1))
        temporal_current_block_architecture = numpy.array(temporal_current_block_architecture)

        temporal_current_architecture = self.base_architecture.copy()
        for y in range(temporal_current_block_architecture.shape[0]):
            for x in range(temporal_current_block_architecture.shape[1]):
                temporal_current_architecture[y + 1][x + 1] += temporal_current_block_architecture[y][x]
                if temporal_current_architecture[y + 1][x + 1] == 2:
                    canMove = False
                    return canMove
        for y in range(self.current_block_architecture.shape[0]):
            if self.current_block_architecture[y][0] == 1:
                canMove = False
                return canMove
        return canMove

    def moveBlockLeftward(self):
        updated_current_block_architecture = []
        for row in self.current_block_architecture:
            updated_current_block_architecture.append(numpy.roll(row, -1))
        self.block_x_position_increment -= 1
        self.current_block_architecture = numpy.array(updated_current_block_architecture).copy()

    def canBlockMoveDownward(self):
        canMove = True

        temporal_current_block_architecture = numpy.array(numpy.roll(self.current_block_architecture, 1, axis = 0))
        temporal_current_architecture = self.base_architecture.copy()

        for y in range(temporal_current_block_architecture.shape[0]):
            for x in range(temporal_current_block_architecture.shape[1]):
                temporal_current_architecture[y + 1][x + 1] += temporal_current_block_architecture[y][x]
                if temporal_current_architecture[y + 1][x + 1] == 2:
                    canMove = False
                    return canMove
        for x in range(self.current_block_architecture.shape[1]):
            if self.current_block_architecture[temporal_current_block_architecture.shape[0] - 1][x] == 1:
                canMove = False
                self.is_current_block_settled = True
                return canMove
        return canMove

    def moveBlockDownward(self):
        updated_current_block_architecture = numpy.array(numpy.roll(self.current_block_architecture, 1, axis = 0))
        self.block_y_position_increment += 1
        self.current_block_architecture = updated_current_block_architecture.copy()

    def canBlockRotate(self):
        canRotate = True

        temporal_current_block_architecture_index = self.current_block_architecture_index
        temporal_current_block_architecture_index += 1
        if temporal_current_block_architecture_index >= len(self.current_block_architectures):
            temporal_current_block_architecture_index = 0
        temporal_current_block_architecture = numpy.array(self.current_block_architectures[temporal_current_block_architecture_index])
        temporal_current_architecture = self.base_architecture.copy()

        updated_current_block_architecture = []
        for row in temporal_current_block_architecture:
            updated_current_block_architecture.append(numpy.roll(row, self.block_x_position_increment))
        temporal_current_block_architecture = numpy.array(updated_current_block_architecture).copy()
        temporal_current_block_architecture = numpy.array(numpy.roll(temporal_current_block_architecture, self.block_y_position_increment, axis = 0))

        for y in range(temporal_current_block_architecture.shape[0]):
            for x in range(temporal_current_block_architecture.shape[1]):
                temporal_current_architecture[y + 1][x + 1] += temporal_current_block_architecture[y][x]
                if temporal_current_architecture[y + 1][x + 1] == 2:
                    canRotate = False
                    return canRotate
        return canRotate

    def rotateBlock(self):
        self.current_block_architecture_index += 1
        if self.current_block_architecture_index >= len(self.current_block_architectures):
            self.current_block_architecture_index = 0
        self.current_block_architecture = self.current_block_architectures[self.current_block_architecture_index]

        updated_current_block_architecture = []
        for row in self.current_block_architecture:
            updated_current_block_architecture.append(numpy.roll(row, self.block_x_position_increment))
        self.current_block_architecture = numpy.array(updated_current_block_architecture).copy()
        self.current_block_architecture = numpy.array(numpy.roll(self.current_block_architecture, self.block_y_position_increment, axis = 0))

    def updateCurrentArchitecture(self):
        self.current_architecture = self.base_architecture.copy()
        for y in range(self.current_block_architecture.shape[0]):
            for x in range(self.current_block_architecture.shape[1]):
                self.current_architecture[y + 1][x + 1] += self.current_block_architecture[y][x]

    def updateCurrentColorArchitecture(self):
        self.current_color_architecture = self.current_architecture.copy()
        for y in range(self.current_architecture.shape[0]):
            for x in range(self.current_architecture.shape[1]):
                if self.current_architecture[y][x] == 1:
                    self.current_color_architecture[y][x] += self.current_block_color_index

    def draw(self):
        self.screen.fill(BLACK)
        self.drawGameFrame()
        self.drawCurrentArchitecture()
        #self.drawCurrentColorArchitecture()
        self.drawGamePlayInfo()
        pygame.display.flip()

    def drawText(self, text, textSize, textCenter, textColor):
        fontName = pygame.font.match_font("arial")
        font = pygame.font.Font(fontName, textSize)
        fontSur = font.render(text, True, textColor)
        fontRect = fontSur.get_rect()
        fontRect.center = textCenter
        self.screen.blit(fontSur, fontRect)

    def drawRect(self, surf, topLeftPos, width, height, color, thickness = 0):
        rect = pygame.Rect(0, 0, width, height)
        rect.topleft = topLeftPos
        pygame.draw.rect(surf, color, rect, thickness)

    def drawGameFrame(self):
        for y in range(self.current_architecture.shape[0]):
            for x in range(self.current_architecture.shape[1]):
                if self.current_architecture[y][x] == 0:
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH / 2 - self.base_architecture.shape[1] * BOX_SIZE / 2, y * BOX_SIZE), BOX_SIZE, BOX_SIZE, WHITE, 1)
                if self.current_architecture[y][x] == 100:
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH / 2 - self.base_architecture.shape[1] * BOX_SIZE / 2, y * BOX_SIZE), BOX_SIZE, BOX_SIZE, WHITE)

    def drawCurrentArchitecture(self):
        for y in range(self.current_architecture.shape[0]):
            for x in range(self.current_architecture.shape[1]):
                if self.current_architecture[y][x] > 0 and self.current_architecture[y][x] < 100:
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH / 2 - self.base_architecture.shape[1] * BOX_SIZE / 2, y * BOX_SIZE), BOX_SIZE, BOX_SIZE, RED)

    def drawCurrentColorArchitecture(self):
        for y in range(self.current_color_architecture.shape[0]):
            for x in range(self.current_color_architecture.shape[1]):
                if self.current_color_architecture[y][x] > 0 and self.current_color_architecture[y][x] < 100:
                    #color = self.available_block_colors[self.current_color_architecture[y][x]]
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH / 2 - self.base_architecture.shape[1] * BOX_SIZE / 2, y * BOX_SIZE), BOX_SIZE, BOX_SIZE, BLUE)

    def drawGamePlayInfo(self):
        self.drawText("Score: ", 50, (SCREEN_WIDTH * 0.8, 100), WHITE)
        self.drawText(str(self.game_score), 50, (SCREEN_WIDTH * 0.87, 100), WHITE)
        self.drawText("Level: ", 50, (SCREEN_WIDTH * 0.8, 200), WHITE)
        self.drawText(str(self.game_level), 50, (SCREEN_WIDTH * 0.85, 200), WHITE)
        self.drawText("Next block: ", 50, (SCREEN_WIDTH * 0.8, 300), WHITE)

        for y in range(self.next_block_architecture.shape[0]):
            for x in range(self.next_block_architecture.shape[1]):
                if self.next_block_architecture[y][x] == 1:
                    self.drawRect(self.screen, (x * BOX_SIZE + SCREEN_WIDTH * 0.85, y * BOX_SIZE + 400), BOX_SIZE, BOX_SIZE, RED)

    def checkGameOverCondition(self):
        gameOver = False
        if 1 in self.base_architecture[1][:]:
            gameOver = True
        return gameOver

    def loadGameOverScene(self):
        self.drawText("Game Over!", 100, (SCREEN_WIDTH / 2, 150), WHITE)
        self.drawText("Your score: " + str(self.game_score), 50, (SCREEN_WIDTH / 2, 400), WHITE)
        self.drawText("You should improve your skill", 50, (SCREEN_WIDTH / 2, 500), WHITE)
        self.drawText("Would you like to continue?", 50, (SCREEN_WIDTH / 2, 600), WHITE)
        self.drawText("Press r to restart", 50, (SCREEN_WIDTH / 2, 800), WHITE)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    elif event.key == pygame.K_s:
                        return True

    def restartGame(self):
        self.base_architecture = numpy.array(BASE_ARCHITECTURE)
        self.current_architecture = self.base_architecture.copy()
        self.current_block_architectures = random.choice([T_SHAPES_ARCHITECTURES, S_SHAPES_ARCHITECTURES, Z_SHAPES_ARCHITECTURES, J_SHAPES_ARCHITECTURES, L_SHAPES_ARCHITECTURES, I_SHAPES_ARCHITECTURES, O_SHAPES_ARCHITECTURES])
        self.current_block_architecture_index = 0
        self.current_block_architecture = numpy.array(self.current_block_architectures[self.current_block_architecture_index])
        self.block_x_position_increment = 0
        self.block_y_position_increment = 0

        self.next_block_architectures = random.choice([T_SHAPES_ARCHITECTURES, S_SHAPES_ARCHITECTURES, Z_SHAPES_ARCHITECTURES, J_SHAPES_ARCHITECTURES, L_SHAPES_ARCHITECTURES, I_SHAPES_ARCHITECTURES, O_SHAPES_ARCHITECTURES])
        self.next_block_architecture_index = 0
        self.next_block_architecture = numpy.array(self.next_block_architectures[self.next_block_architecture_index])

        self.base_color_architecture = self.base_architecture.copy()
        self.current_color_architecture = self.base_architecture.copy()
        self.available_block_colors = [RED, GREEN, BLUE, YELLOW]
        self.available_block_light_colors = [LIGHTRED, LIGHTGREEN, LIGHTBLUE, LIGHTYELLOW]
        self.current_block_color_index = random.randint(0, len(self.available_block_colors))

    def updateScheduler(self):
        now = self.time.get_ticks()
        if now - self.last_scheduler_update_time > self.scheduler_update_delay:
            self.last_scheduler_update_time = now
            #print(self.current_color_architecture)

if __name__ == "__main__":
    g = Game()
    if g.loadIninitalScene():
        g.run()
