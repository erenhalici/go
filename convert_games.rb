# encoding: utf-8

require 'set'
require './converter/game.rb'

puts

GAMESDIR = '/Users/erenhalici/Academic/tensorflow/usr/go/games'
OUTPUTDIR = '/Users/erenhalici/Academic/tensorflow/usr/go/data/moves_single'

def convert_board(board, lost_pieces, komi, player)
  count = 0

  if (lost_pieces < 0)
    lost_count_b = 0
    lost_count_w = -lost_pieces
  else
    lost_count_b = lost_pieces
    lost_count_w = 0
  end

  komi = komi*2

  flat = []

  board.each do |row|
    row.each do |e|
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

      if count < komi
        k = 1
      else
        k = 0
      end

      count += 1

      if e == BLACK
        flat.push(*[1, 0, 0, 0, lost_b, lost_w, k, player])
      elsif e == WHITE
        flat.push(*[0, 1, 0, 0, lost_b, lost_w, k, player])
      elsif e == KO
        flat.push(*[0, 0, 1, 0, lost_b, lost_w, k, player])
      else
        flat.push(*[0, 0, 0, 1, lost_b, lost_w, k, player])
      end
    end
  end

  return flat
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

  # if game.win_by_time
  #   return false
  # end

  if (game.komi*2) % 1 != 0.0
    return false
  end

  # if game.moves.count < 100
  #   return false
  # end

  if game.white_rank && game.white_rank > 7 && game.black_rank && game.black_rank > 7
    return true
  end

  return false
end

def convert_move(move)
  move[0] * 19 + move[1]
end

def enumerate_games
  total = 0
  count = 0

  games = Set.new

  Dir.glob(GAMESDIR + '/**/*.sgf').each do |filename|
    puts total if total%10000 == 0
    game = Game.new(filename)
    if game.valid?
      if filter(game)
        if games.add?(game.moves.hash)
          yield game
          count +=1
        end
      end
    end
    total += 1
  end
end

def move_combinations(move)
  yield move
  yield [18-move[0], move[1]]
  yield [18-move[0], 18-move[1]]
  yield [move[0], 18-move[1]]

  yield [move[1], move[0]]
  yield [18-move[1], move[0]]
  yield [18-move[1], 18-move[0]]
  yield [move[1], 18-move[0]]
end

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

moves = []
enumerate_games do |game|
  game.moves.count.times do |index|
    move = game.moves[index]
    if move
      # move_combinations(move) do |m|
      #   moves << convert_move(m)
      # end
      moves << convert_move(move)
    end
  end
end

moves_count = moves.count

File.open(OUTPUTDIR + '/labels.dat', 'w') do |f|
  f.write([moves_count].pack('N'))
  f.write(moves.pack('n*'))
end

moves = nil

puts "#{moves_count} moves"

total_moves = 0
File.open(OUTPUTDIR + '/games.dat', 'w') do |f|
  f.write([moves_count].pack('N'))

  enumerate_games do |game|
    index = 0
    game.enumerate_board_states do |result|
      # board_combinations(result[:board]) do |board|
      #   f.write(convert_board(board, result[:captured], result[:komi], result[:player]).pack('C*'))
      #   total_moves += 1
      # end
      f.write(convert_board(result[:board], result[:captured], result[:komi], result[:player]).pack('C*'))
      total_moves += 1
      index += 1
    end
  end
end

puts "#{total_moves} moves"
