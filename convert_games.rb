# encoding: utf-8

require 'set'
require './converter/game.rb'

puts

GAMESDIR = '/Users/erenhalici/Academic/tensorflow/usr/go/games'
OUTPUTDIR = '/Users/erenhalici/Academic/tensorflow/usr/go/data/winner_ko'

def convert_board(board, captured, komi)
  count = 0

  captured -= komi
  captured = captured * 2

  if (captured < 0)
    lost_count_b = 0
    lost_count_w = -captured
  else
    lost_count_b = captured
    lost_count_w = 0
  end

  board.map do |row|
    row.map do |e|
      if count < lost_count_b
        lost_b = 1
      else
        lost_b = 0
      end

      if count < lost_count_w
        lost_w = 1
      else
        lost_w = 0
      end

      count += 1

      if e == BLACK
        [1, 0, 0, 0, lost_b, lost_w]
      elsif e == WHITE
        [0, 1, 0, 0, lost_b, lost_w]
      elsif e == KO
        [0, 0, 1, 0, lost_b, lost_w]
      else
        [0, 0, 0, 1, lost_b, lost_w]
      end
    end
  end
end

def convert_winner(winner)
  if winner == 'B'
    0
  else
    1
  end
end

def filter(game)
  if game.size && game.size != '19'
    return false
  end

  if game.date && Time.new(game.date).year < 1970
    return false
  end

  if !game.winner
    return false
  end

  if game.win_by_time
    return false
  end

  if (game.komi*2) % 1 != 0.0
    return false
  end

  if game.moves.count < 100
    return false
  end

  return true
end


def enumerate_games
  total = 0
  count = 0
  games = Set.new

  Dir.glob(GAMESDIR + '/**/*.sgf').each do |filename|
    total += 1
    puts total if total%10000 == 0

    game = Game.new(filename)
    if game.valid?
      if filter(game)
        if games.add?(game.moves.hash)
          yield game
          count += 1
        end
      end
    end
  end

  puts count
  puts total
end

labels = []

enumerate_games do |game|
  8.times {labels << convert_winner(game.winner)}
end

File.open(OUTPUTDIR + '/labels.dat', 'w') do |f|
  f.write([labels.count].pack('N'))
  f.write(labels.pack('C*'))
end

puts labels.count

def board_combinations(board)
  yield board
  yield board.reverse
  yield (board.map{|row| row.reverse}).reverse
  yield board.map{|row| row.reverse}

  yield board.transpose
  yield board.transpose.reverse
  yield (board.transpose.map{|row| row.reverse}).reverse
  yield board.transpose.map{|row| row.reverse}
end

File.open(OUTPUTDIR + '/games.dat', 'w') do |f|
  f.write([labels.count].pack('N'))
  # f.write([819464].pack('N'))

  enumerate_games do |game|
    result = game.result
    board_combinations(result[:board]) do |board|
      f.write([convert_board(board, result[:captured], result[:komi])].flatten.pack('C*'))
    end
  end
end


# max = 0
# min = 10000


# if count < 2
  # begin
  #   endgame = parsefile(file)
  #   if endgame
  #     board_str = endgame[:board].flatten.join('|')
  #     if !games[board_str]
  #       games[board_str] = true

  #       count += 1
  #       # endgames << endgame
  #       board = endgame[:board]
  #       # endgames << {board: board.map{|row| row.reverse}, result: endgame[:result]}

  #       # boards << convert_board(board)
  #       # labels << convert_result(endgame[:result])
  #       # boards << convert_board(board.reverse)
  #       # labels << convert_result(endgame[:result])
  #       # boards << convert_board((board.map{|row| row.reverse}).reverse)
  #       # labels << convert_result(endgame[:result])
  #       # boards << convert_board(board.map{|row| row.reverse})
  #       # labels << convert_result(endgame[:result])

  #       # boards << convert_board(board.transpose)
  #       # labels << convert_result(endgame[:result])
  #       # boards << convert_board(board.transpose.reverse)
  #       # labels << convert_result(endgame[:result])
  #       # boards << convert_board((board.transpose.map{|row| row.reverse}).reverse)
  #       # labels << convert_result(endgame[:result])
  #       # boards << convert_board(board.transpose.map{|row| row.reverse})
  #       # labels << convert_result(endgame[:result])

  #       # boards << convert_board(board, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])
  #       # boards << convert_board(board.reverse, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])
  #       # boards << convert_board((board.map{|row| row.reverse}).reverse, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])
  #       # boards << convert_board(board.map{|row| row.reverse}, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])

  #       # boards << convert_board(board.transpose, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])
  #       # boards << convert_board(board.transpose.reverse, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])
  #       # boards << convert_board((board.transpose.map{|row| row.reverse}).reverse, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])
  #       # boards << convert_board(board.transpose.map{|row| row.reverse}, endgame[:lost_pieces], endgame[:komi])
  #       labels << convert_winner(endgame[:winner])


  #       # boards << convert_board(board, endgame[:lost_pieces], endgame[:komi])
  #       # labels << convert_winner(endgame[:winner])


  #       # lost_pieces = endgame[:lost_pieces]
  #       # if lost_pieces > max
  #       #   max = lost_pieces
  #       #   puts "new max: #{max}"
  #       # end

  #       # if lost_pieces < min
  #       #   min = lost_pieces
  #       #   puts "new min: #{min}"
  #       # end
  #     end
  #   end
#     game = Game.new(filename)
#     if game.valid?
#       if filter(game)
#         if games.add?(game.moves.hash)
#           # game.moves.count.times do |move|
#           #   puts "------ Captured: #{game.captured} -------------------------"
#           #   game.print_board(game.board_for_move(move))
#           # end

#           # puts game.result
#           game.result

#           count += 1

#           if count == 29
#             1/0
#           end
#         end
#       end
#     end
#   # rescue
#   # end
# # end
# end

# puts max
# puts min

# endgames.shuffle.each do |endgame|
#   boards << convert_board(endgame[:board])
#   labels << convert_result(endgame[:result])
# end

# File.open(OUTPUTDIR + '/games.dat', 'w') do |f|
#   f.write([boards.count].pack('N'))
#   f.write(boards.flatten.pack('C*'))
# end

# File.open(OUTPUTDIR + '/labels.dat', 'w') do |f|
#   f.write([labels.count].pack('N'))
#   f.write(labels.pack('C*'))
# end

# puts boards[0][0].map{|e| e.join('')}.join("\n")
