import numpy as np
import torch
from .board import Board, Piece


class BoardEncoder:
    """棋盘编码器 - 将棋盘转为神经网络输入"""

    CHANNEL_MAP = {
        # 红方棋子 (0-6)
        (Piece.KING, Piece.RED): 0,
        (Piece.ADVISOR, Piece.RED): 1,
        (Piece.ELEPHANT, Piece.RED): 2,
        (Piece.HORSE, Piece.RED): 3,
        (Piece.CHARIOT, Piece.RED): 4,
        (Piece.CANNON, Piece.RED): 5,
        (Piece.PAWN, Piece.RED): 6,
        # 黑方棋子 (7-13)
        (Piece.KING, Piece.BLACK): 7,
        (Piece.ADVISOR, Piece.BLACK): 8,
        (Piece.ELEPHANT, Piece.BLACK): 9,
        (Piece.HORSE, Piece.BLACK): 10,
        (Piece.CHARIOT, Piece.BLACK): 11,
        (Piece.CANNON, Piece.BLACK): 12,
        (Piece.PAWN, Piece.BLACK): 13,
    }

    @staticmethod
    def encode(board: Board, history_boards: list = None) -> np.ndarray:
        """
        编码棋盘为56通道 (14 x 4)张量
        """
        planes = np.zeros((56, 10, 9), dtype=np.float32)

        # 当前局面
        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece:
                    channel = BoardEncoder.CHANNEL_MAP.get((piece[0], piece[1]))
                    if channel is not None:
                        planes[channel, r, c] = 1

        # 历史局面 (最多3步)
        if history_boards:
            for i, hist_board in enumerate(history_boards[:3]):
                offset = (i + 1) * 14
                for r in range(10):
                    for c in range(9):
                        piece = hist_board.board[r][c]
                        if piece:
                            channel = BoardEncoder.CHANNEL_MAP.get((piece[0], piece[1]))
                            if channel is not None:
                                planes[offset + channel, r, c] = 1

        return planes

    @staticmethod
    def encode_to_tensor(board: Board, history_boards: list = None) -> torch.Tensor:
        """编码为PyTorch张量 [1, 56, 10, 9]"""
        planes = BoardEncoder.encode(board, history_boards)
        return torch.from_numpy(planes).unsqueeze(0)
