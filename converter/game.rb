
require './converter/board'

class Game
  attr_reader :input, :moves, :size, :date, :winner, :win_by_time, :komi,
              :white_rank, :black_rank, :info, :captured

  def initialize(filename)
    @captured = 0
    @valid = true

    f = File.open(filename)
    @input = f.read.encode('UTF-8', :invalid => :replace).gsub('(KGS)', '')
    f.close
    tokens = @input.split(';')

    parse_info(tokens)
    parse_moves(tokens) if @valid
  end

  def parse_info(tokens)
    @info = tokens[1]

    @size = @info[/SZ\[([^\]]*)\]/, 1]
    @date = @info[/DT\[([^\]]*)\]/, 1]

    @black_rank = @info[/BR\[(\d)d\]/, 1]
    @white_rank = @info[/WR\[(\d)d\]/, 1]

    if @black_rank
      @black_rank = @black_rank.to_i
    end

    if @white_rank
      @white_rank = @white_rank.to_i
    end

    @winner = @info[/RE\[([BW])\+/, 1]
    # @result = @info[/RE\[[BW]\+(\d+(.\d+)?)\]/, 1]
    @result = @info[/RE\[[BW]\+([^\]]*)\]/, 1]

    if @result
      if @result[0] == 'T' || @result[0] == 't'
        @win_by_time = true
      end
    end

    @komi = @info[/KM\[([^\]]*)\]/, 1]
    @komi = @komi ? @komi.to_f : 0.0

    add = input[/A[BW]\[(.*)\]/, 1]
    if add
      @valid = false
      return
    end
    if input.count('(') != 1
      @valid = false
      return
    end
    if input.count(')') != 1
      @valid = false
      return
    end
  end

  def parse_moves(tokens)
    @moves = []

    current_player = 'B'

    while !tokens.empty?
      move = tokens.shift
      player = move[/^[^A-Z]*([BW])\[([^\]]*)\]/, 1]
      location = move[/^[^A-Z]*([BW])\[([^\]]*)\]/, 2]

      if player
        if player != current_player
          @valid = false
          return
        end

        if location != ''
          row = location[1].ord - 'a'.ord
          col = location[0].ord - 'a'.ord

          if row < 0 || row >= 19 || col < 0 || col >= 19
            @valid = false
            return
          end

          @moves << [row, col]
        else
          @moves << nil
        end

        current_player = (current_player == 'B') ? 'W' : 'B'
      end
    end
  end

  def remove(board, row, col, type)
    total = 0
    if board[row][col] == type
      total = 1
      board[row][col] = FREE
      total += remove(board, row - 1, col, type) if row > 0
      total += remove(board, row + 1, col, type) if row < 18
      total += remove(board, row, col - 1, type) if col > 0
      total += remove(board, row, col + 1, type) if col < 18
    end
    return total
  end

  def dead?(board, row, col, type, visited)
    return false if board[row][col] == FREE
    return true if board[row][col] != type

    return true if visited[[row,col]]
    visited[[row,col]] = true

    return false if row > 0  && !dead?(board, row - 1, col, type, visited)
    return false if row < 18 && !dead?(board, row + 1, col, type, visited)
    return false if col > 0  && !dead?(board, row, col - 1, type, visited)
    return false if col < 18 && !dead?(board, row, col + 1, type, visited)

    return true
  end

  def sanitize_board(board, row, col)
    if board[row][col] == FREE
      return 0
    end

    if dead?(board, row, col, board[row][col], {})
      return ((board[row][col] == BLACK) ? -1 : 1) * remove(board, row, col, board[row][col])
    end

    return 0
  end

  def clear_ko(board)
    if @last_ko_row && @last_ko_col && board[@last_ko_row][@last_ko_col] == KO
      board[@last_ko_row][@last_ko_col] = FREE

      @last_ko_row = nil
      @last_ko_col = nil
    end
  end

  def check_ko(board, row, col, type)
    if board[row][col] != FREE
      liberties = 0

      liberties += 1 if row > 0  && (board[row - 1][col] == FREE || board[row - 1][col] == type)
      liberties += 1 if row < 18 && (board[row + 1][col] == FREE || board[row + 1][col] == type)
      liberties += 1 if col > 0  && (board[row][col - 1] == FREE || board[row][col - 1] == type)
      liberties += 1 if col < 18 && (board[row][col + 1] == FREE || board[row][col + 1] == type)

      if liberties == 1
        if row > 0  && board[row - 1][col] == FREE
          board[row - 1][col] = KO
          @last_ko_row = row - 1
          @last_ko_col = col
        end

        if row < 18 && board[row + 1][col] == FREE
          board[row + 1][col] = KO
          @last_ko_row = row + 1
          @last_ko_col = col
        end

        if col > 0  && board[row][col - 1] == FREE
          board[row][col - 1] = KO
          @last_ko_row = row
          @last_ko_col = col - 1
        end

        if col < 18 && board[row][col + 1] == FREE
          board[row][col + 1] = KO
          @last_ko_row = row
          @last_ko_col = col + 1
        end
      end
    end
  end

  def make_move(board, index)
    clear_ko board

    move = @moves[index]

    if !move
      return
    end

    row = move[0]
    col = move[1]

    type = (index%2 == 0) ? BLACK : WHITE

    board[row][col] = type

    total = 0

    total += sanitize_board(board, row - 1, col) if row > 0  && board[row - 1][col] != type
    total += sanitize_board(board, row + 1, col) if row < 18 && board[row + 1][col] != type
    total += sanitize_board(board, row, col - 1) if col > 0  && board[row][col - 1] != type
    total += sanitize_board(board, row, col + 1) if col < 18 && board[row][col + 1] != type

    total += sanitize_board(board, row, col) if total == 0

    if total == -1 || total == 1
      check_ko board, row, col, type
    end

    @captured += total
  end

  def print_board(board)
    puts (board.map{ |row| row.join(' ') }).join("\n")
  end

  def board_for_move(move)
    board = Board.new_board
    @captured = 0

    move.times do |index|
      make_move(board, index)
    end

    return board
  end

  def enumerate_board_states
    board = Board.new_board
    @captured = 0

    results = []

    @moves.count.times do |index|
      if @moves[index]
        yield ({board: board, komi: @komi, captured: @captured, player: (index % 2)})
      end

      make_move(board, index)
    end
  end

  def result
    {board: board_for_move(@moves.count), komi: @komi, captured: @captured, player: (@moves.count % 2)} # check if correct
  end

  def valid?
    @valid
  end
end
