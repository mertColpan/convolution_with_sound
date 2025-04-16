# Gerekli kütüphaneler içe aktarılıyor
import numpy as np
import sounddevice as sd
import time 
import matplotlib.pyplot as plt

# Elle konvolüsyon işlemi gerçekleştiren fonksiyon
def myConv(x, n, y, m):
    result_len = n + m - 1  # Sonuç sinyalinin uzunluğu
    result = np.zeros(result_len, dtype=np.float32)

    # y sinyalinde sıfır olmayan elemanları sakla (verimlilik için)
    nonzero_y = [(j, y[j]) for j in range(m) if y[j] != 0]

    # Konvolüsyon işlemi
    for i in range(n):
        for j, yj in nonzero_y:
            if 0 <= i + j < result_len:
                result[i + j] += x[i] * yj

    return result

# Konsolda sinyali indeksleriyle birlikte yazdıran fonksiyon
def print_with_underline(signal, start_index):
    signal_strs = [f"{val:.2f}" for val in signal]
    positions = list(range(start_index, start_index + len(signal)))

    output_line = ""
    underline_line = ""

    for i, (val_str, pos) in enumerate(zip(signal_strs, positions)):
        output_line += f"{val_str:>6}"
        if pos == 0:
            underline_line += "  " + "‾" * (len(val_str)) + "  "
        else:
            underline_line += " " * 6

    print("Indeks : ", ' '.join([f"{i:>5}" for i in positions]))
    print("Sinyal: ", output_line)
    print("        ", underline_line)

# Konvolüsyon sonuçlarını grafikle karşılaştırmak için fonksiyon
def plot_convolution_comparison(x, y, my_result, np_result, set_name, x_start=0, y_start=0):
    result_start = x_start + y_start

    fig, axs = plt.subplots(1, 4, figsize=(16, 4))
    fig.suptitle(f"{set_name} - Konvolüsyon Karşılaştırması", fontsize=14)

    axs[0].stem(range(x_start, x_start + len(x)), x)
    axs[0].set_title("x[n]")
    axs[0].grid(True)

    axs[1].stem(range(y_start, y_start + len(y)), y)
    axs[1].set_title("y[m]")
    axs[1].grid(True)

    axs[2].stem(range(result_start, result_start + len(my_result)), my_result)
    axs[2].set_title("myConv(x, n, y, m)")
    axs[2].grid(True)

    axs[3].stem(range(result_start, result_start + len(np_result)), np_result)
    axs[3].set_title("np.convolve(x, n, y, m)")
    axs[3].grid(True)

    plt.tight_layout()
    plt.show()

# Vektör değerlerini yazdıran yardımcı fonksiyon
def print_convolution_vectors(x, y, my_result, np_result, set_name):
    print(f"\n=== {set_name} ===")
    print(f"x[n]            : {x}")
    print(f"y[m]            : {y}")
    print(f"myConv sonucu   : {my_result}")
    print(f"np.convolve     : {np_result}")

# Kullanıcıdan sinyal girdisi alma fonksiyonu
def take_signals(len_x, start_indice_x):
    x = np.zeros(len_x, dtype = np.float64)
    for i in range(len_x):
        x[i] = int(input(f'{start_indice_x + i}. value: '))
    return x 

# Mikrofon ile ses kaydı alma fonksiyonu
def record_voice(fs, duration):
    x = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # Kayıt bitene kadar bekle
    return x

# Kaydedilen sesi oynatma fonksiyonu
def play_voice(x, fs):
    sd.play(x, samplerate=fs, blocking=True)
    sd.wait()  # Ses çalması bitene kadar bekle

# Darbe (impulse) cevabı oluşturan fonksiyon
def create_impulse_signal(m):
    impulse = np.zeros(((400 * m) + 1))  # Uzunluk belirleniyor
    A = 0.5
    impulse[0] = 1
    for i in range(1, m + 1):
        impulse[i * 400] = A * i
    return impulse

# Verilen ses sinyali için konvolüsyon uygulanması ve çalınması
def apply_and_save_all_versions(X, name, fs):
    for M in [3, 4, 5]:
        print(f"\n--- {name} için M = {M} işlemi ---")
        h = create_impulse_signal(M)  # Sistem darbe cevabı
        myY = myConv(X, len(X), h, len(h))  # myConv ile çıktı
        Y = np.convolve(X, h)  # numpy ile konvolüsyon
        play_voice(X.reshape(-1, 1), fs)  # Orijinal ses
        play_voice(myY.reshape(-1, 1), fs)  # myConv sonucu
        play_voice(Y.reshape(-1, 1), fs)  # np.convolve sonucu
        plot_convolution_comparison(X, h, myY, Y, f"{name} M={M}")

# Görev 1: Kullanıcıdan sinyal al, konvolüsyon yap, yazdır
def q1():
    len_x = int(input('Birinci sinyal giriş boyutunu giriniz: '))
    start_indice_x = int(input('Birinci sinyalin başlama indisini giriniz: '))
    len_y = int(input('İkinci sinyal giriş boyutunu giriniz: '))
    start_indice_y = int(input('İkinci sinyalin başlama indisini giriniz: '))
    
    print('Birinci sinyal değerleri: ')
    x = take_signals(len_x, start_indice_x)

    print('\nİkinci sinyal değerleri: ')
    y = take_signals(len_y, start_indice_y)

    print('\n--- x[n] ---')
    print_with_underline(x, start_indice_x)

    print('\n--- y[m] ---')
    print_with_underline(y, start_indice_y)

    result = myConv(x, len(x), y, len(y))
    result_start_indice = start_indice_x + start_indice_y

    print('\n--- x[n] * y[m] Sonuç ---')
    print_with_underline(result, result_start_indice)

# Görev 2: İki hazır veri seti ile konvolüsyon karşılaştırması
def q2():
    # Veri Seti 1
    x1 = np.array([1, 2, 3])
    y1 = np.array([0, 1, 0.5])
    start_x1 = 0
    start_y1 = -1
    my_result1 = myConv(x1, len(x1), y1, len(y1))
    np_result1 = np.convolve(x1, y1)
    result1_start = start_x1 + start_y1
    print(f"\n=== Veri Seti 1 ===")
    print("x[n]:")
    print_with_underline(x1, start_x1)
    print("y[m]:")
    print_with_underline(y1, start_y1)
    print("myConv(x, n, y, m):")
    print_with_underline(my_result1, result1_start)
    print("np.convolve(x, n, y, m):")
    print_with_underline(np_result1, result1_start)
    plot_convolution_comparison(x1, y1, my_result1, np_result1, "Veri Seti 1", start_x1, start_y1)

    # Veri Seti 2
    x2 = np.array([2, -1, 3, 0])
    y2 = np.array([1, 2])
    start_x2 = -2
    start_y2 = 0
    my_result2 = myConv(x2, len(x2), y2, len(y2))
    np_result2 = np.convolve(x2, y2)
    result2_start = start_x2 + start_y2
    print(f"\n=== Veri Seti 2 ===")
    print("x[n]:")
    print_with_underline(x2, start_x2)
    print("y[m]:")
    print_with_underline(y2, start_y2)
    print("myConv(x, n, y, m):")
    print_with_underline(my_result2, result2_start)
    print("np.convolve(x, n, y, m):")
    print_with_underline(np_result2, result2_start)
    plot_convolution_comparison(x2, y2, my_result2, np_result2, "Veri Seti 2", start_x2, start_y2)

# Görev 3: İki ses kaydı al
def q3():
    fs = 44100
    duration_1 = 5
    duration_2 = 10
    print("X1 kaydediliyor...")
    X1 = record_voice(fs, duration_1).flatten()
    print("X1 kaydı tamamlandı.")
    print("5 saniye bekleniyor...")
    time.sleep(5)
    print("X2 kaydediliyor...")
    X2 = record_voice(fs, duration_2).flatten()
    print("X2 kaydı tamamlandı.")

# Görev 4: Kaydedilen seslere konvolüsyon uygulayıp oynat
def q4():
    fs = 44100
    duration_1 = 5
    duration_2 = 10
    print("X1 kaydediliyor...")
    X1 = record_voice(fs, duration_1).flatten()
    print("X1 kaydı tamamlandı.")
    print("5 saniye bekleniyor...")
    time.sleep(5)
    print("X2 kaydediliyor...")
    X2 = record_voice(fs, duration_2).flatten()
    print("X2 kaydı tamamlandı.")
    apply_and_save_all_versions(X1, "X1", fs)  # X1’e uygulama
    apply_and_save_all_versions(X2, "X2", fs)  # X2’ye uygulama

# Ana fonksiyon
def main():
    print("Birinci görev başlatılıyor ...")
    q1()
    print("Birinci görev bitti")

    print("\n5 saniye bekleniyor ...")
    time.sleep(5)

    print("\nİkinci görev başlatılıyor ...")
    q2()
    print("İkinci görev bitti")

    print("\n5 saniye bekleniyor ...")
    time.sleep(5)

    print("\nÜçüncü görev başlatılıyor ...")
    q3()
    print("Üçüncü görev bitti")

    print("\n5 saniye bekleniyor ...")
    time.sleep(5)

    print("\nDördüncü görev başlatılıyor ...")
    q4()    
    print("Dördüncü görev bitti")

    print("Görevler bitmiştir")
    print("5 saniye sonra sistem kapanacaktır")
    time.sleep(5)

# Program çalıştırma noktası
if __name__ == "__main__":
    main()
