from board import TTTBoardDecision, GridStates, TTTBoard
from ultimateboard import UTTTBoard, UTTTBoardDecision
from player import RandomTTTPlayer, RLTTTPlayer
from ultimateplayer import RandomUTTTPlayer, RLUTTTPlayer
from learning import NNUltimateLearning
from plotting import drawXYPlotByFactor
import os

LEARNING_FILE = 'ultimate_player_nn1.h5'
WIN_PCT_FILE = 'win_pct_player_1.csv'

class GameSequence(object):
    def __init__(self, numberOfGames, player1, player2, BoardClass=TTTBoard, BoardDecisionClass=TTTBoardDecision):
        self.player1 = player1
        self.player2 = player2
        self.numberOfGames = numberOfGames
        self.BoardClass = BoardClass
        self.BoardDecisionClass = BoardDecisionClass

    def playAGame(self, board):
        while board.getBoardDecision() == self.BoardDecisionClass.ACTIVE:
            self.player1.setBoard(board, GridStates.PLAYER_X)
            self.player2.setBoard(board, GridStates.PLAYER_O)
            pState1 = self.player1.makeNextMove()
            self.player1.learnFromMove(pState1)
            self.player2.learnFromMove(pState1)
            pState2 = self.player2.makeNextMove()
            self.player1.learnFromMove(pState2)
            self.player2.learnFromMove(pState2)
        return board.getBoardDecision()

    def playGamesAndGetWinPercent(self):
        results = []
        for i in range(self.numberOfGames):
            board = self.BoardClass()
            results.append(self.playAGame(board))
        xpct, opct, drawpct = float(results.count(self.BoardDecisionClass.WON_X))/float(self.numberOfGames), \
                              float(results.count(self.BoardDecisionClass.WON_O))/float(self.numberOfGames), \
                              float(results.count(self.BoardDecisionClass.DRAW))/float(self.numberOfGames)
        return (xpct, opct, drawpct)

def playTTTAndPlotResults():
    learningPlayer = RLTTTPlayer()
    randomPlayer = RandomTTTPlayer()
    results = []
    numberOfSetsOfGames = 40
    for i in range(numberOfSetsOfGames):
        games = GameSequence(100, learningPlayer, randomPlayer)
        results.append(games.playGamesAndGetWinPercent())
    plotValues = {'X Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[0], results)),
                  'O Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[1], results)),
                  'Draw Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[2], results))}
    drawXYPlotByFactor(plotValues, 'Set Number', 'Fraction')

def playUltimateAndPlotResults():
    learningPlayer = RLUTTTPlayer(NNUltimateLearning)
    randomPlayer = RandomUTTTPlayer()
    results = []
    numberOfSetsOfGames = 40
    if os.path.isfile(LEARNING_FILE):
        learningPlayer.loadLearning(LEARNING_FILE)
    for i in range(numberOfSetsOfGames):
        games = GameSequence(100, learningPlayer, randomPlayer, BoardClass=UTTTBoard, BoardDecisionClass=UTTTBoardDecision)
        results.append(games.playGamesAndGetWinPercent())
    learningPlayer.saveLearning(LEARNING_FILE)
    writeResultsToFile(results)
    plotValues = {'X Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[0], results)),
                  'O Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[1], results)),
                  'Draw Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[2], results))}
    drawXYPlotByFactor(plotValues, 'Set Number', 'Fraction')

def writeResultsToFile(results):
    with open(WIN_PCT_FILE, 'a') as outfile:
        for result in results:
            outfile.write('%s,%s,%s\n'%(result[0], result[1], result[2]))

if __name__ == '__main__':
    #playTTTAndPlotResults()
    playUltimateAndPlotResults()