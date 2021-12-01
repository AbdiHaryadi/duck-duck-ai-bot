def update_border(game_state, border_list):
    """
    Return border_list terbaru.
    Proses: untuk mencari hal yang baru, cek tile dari border_list
    apakah ada city tile di situ. Jika ada, expand ke luar dan
    anggap itu sebagai border_list baru. Return border_list baru.
    """
    return border_list