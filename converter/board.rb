
# FREE = ' '
# BLACK = 'B'
# WHITE = 'W'
FREE = ' '
BLACK = '•'
WHITE = 'o'
KO = 'X'

class Board
  def Board.new_board
    board = []

    19.times do
      row = []
      19.times do
        row << FREE
      end
      board << row
    end

    return board
  end

  def Board.invert_board(board)
    board.map do |row|
      row.map do |type|
        if type == BLACK
          WHITE
        elsif type == WHITE
          BLACK
        else
          type
        end
      end
    end
  end



  def Board.black_capture_count(board)
    19.times do |row|
      19.times do |col|
        if board[row][col] == BLACK

        end
      end
    end
  end
end