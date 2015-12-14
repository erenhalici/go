# encoding: utf-8

puts

GAMESDIR = '/Users/erenhalici/Academic/tensorflow/usr/go/games'
OUTPUTDIR = '/Users/erenhalici/Academic/tensorflow/usr/go/data'

FREE = ' '
BLACK = '•'
WHITE = 'o'

count = 0

def new_board
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

def make_move(board, player, row, col)
  board[row][col] = (player) ? BLACK : WHITE

  total = 0

  total += sanitize_board(board, row - 1, col) if row > 0
  total += sanitize_board(board, row + 1, col) if row < 18
  total += sanitize_board(board, row, col - 1) if col > 0
  total += sanitize_board(board, row, col + 1) if col < 18

  return total
end

def parsefile(file)
  f = File.open(file)
  input = f.read.encode('UTF-8', :invalid => :replace)
  f.close
  tokens = input.split(';')
  info = tokens[1]

  size = info[/SZ\[([^\]]*)\]/, 1]

  if size && size != '19'
    return nil
  end

  winner = info[/RE\[([BW])\+/, 1]
  result = info[/RE\[[BW]\+(\d+(.\d+)?)\]/, 1]

  if !result
    return nil
  end

  # puts input

  result = result.to_f

  if winner == 'W'
    result = -result
  end

  komi = info[/KM\[([^\]]*)\]/, 1]

  # return komi

  # if komi != '5.5'
  #   return nil
  # end

  if komi
    komi = komi.to_f
  else
    komi = 0.0
  end

  result += komi.to_f

  if result % 1 != 0.0
    return nil
  end

  add = input[/A[BW]\[(.*)\]/, 1]

  if add
    return nil
  end

  if input.count('(') != 1
    return nil
  end

  if input.count(')') != 1
    return nil
  end

  board = new_board

  lost_pieces = 0

  while !tokens.empty?
    move = tokens.shift
    player = move[/^[^A-Z]*([BW])\[([^\]]*)\]/, 1]
    location = move[/^[^A-Z]*([BW])\[([^\]]*)\]/, 2]

    if player
      lost_pieces += make_move(board, player=='B', location[1].ord - 'a'.ord, location[0].ord - 'a'.ord)
    end
  end


  result = result - lost_pieces
  # puts board.map{|e| e.join('')}.join("\n")
  # puts "pieces: #{lost_pieces}"
  # puts "board state: #{result - lost_pieces}"
  # puts "komi: #{komi}"
  # puts result
  # puts board.map{|e| e.join('')}.join("\n")
  return {board: board, result: result}
end


def convert_board(board)
  board.map do |row|
    row.map do |e|
      if e == BLACK
        [1, 0]
      elsif e == WHITE
        [0, 1]
      else
        [0, 0]
      end
    end
  end
end

def convert_result(result)
  if result < -5
    0
  elsif result < -3
    1
  elsif result < -1
    2
  elsif result <= 1
    3
  elsif result <= 3
    4
  elsif result <= 5
    5
  elsif result <= 7
    6
  elsif result <= 9
    7
  elsif result <= 11
    8
  else
    9
  end
end

total = 0
boards = []
labels = []
Dir.glob(GAMESDIR + '/**/*.sgf').each do |file|
  total += 1

  puts total if total%1000 == 0
# if count < 2
  begin
    endgame = parsefile(file)
    if endgame
      count += 1
      boards << convert_board(endgame[:board])
      labels << convert_result(endgame[:result])
    end
  rescue
  end
# end
end

File.open(OUTPUTDIR + '/games.dat', 'w') do |f|
  f.write([boards.count].pack('N'))
  f.write(boards.flatten.pack('C*'))
end

File.open(OUTPUTDIR + '/labels.dat', 'w') do |f|
  f.write([labels.count].pack('N'))
  f.write(labels.pack('C*'))
end

# puts boards[0][0].map{|e| e.join('')}.join("\n")

puts count
puts total