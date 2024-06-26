"""Calibration Curve

Draw a calibration curve.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import skimage as ski
import statistics
from natsort import natsorted


def load_images(folder_name):
  """Load images in the folder."""
  folder_path = os.path.join(os.getcwd(), folder_name)
  list_files = os.listdir(folder_path)
  list_files = natsorted(list_files)
  images = []
  for filename in list_files:
    file_path = os.path.join(folder_path, filename)
    images.append(ski.io.imread(file_path))
  return images

def get_rgb(img):
  """Get the average RGB of an image."""
  # Create a mask for white regions
  white_mask = np.all(img == [255, 255, 255], axis=-1)
  # Invert the mask to select non-white regions
  non_white_mask = ~white_mask
  # Extract non-white pixels from the image
  non_white_pixels = img[non_white_mask]
  # Calculate the average RGB values for non-white regions
  average_rgb = np.mean(non_white_pixels, axis=0)
  normalized_rgb = [i*100/255 for i in average_rgb]
  return normalized_rgb

def rgb_stdev(imgs):
  """Get the average RGB and standard deviation of images."""
  rgbs = [get_rgb(i) for i in imgs]
  rs = [i[0] for i in rgbs]
  gs = [i[1] for i in rgbs]
  bs = [i[2] for i in rgbs]
  average_rgb = [statistics.mean(rs), statistics.mean(gs), statistics.mean(bs)]
  st_dev = [statistics.stdev(rs), statistics.stdev(gs), statistics.stdev(bs)]
  return average_rgb, st_dev, rgbs

def comparison(images, concentration_range):
  """Display the result of comparison and the RGB value of each one."""
  # Remove background
  # Show RGB values
  concentrations = concentration_range
  rgb = []
  sd = []
  rgbs = []
  for i in images:
    color, st_dev, colors = rgb_stdev(i)
    rgb.append(color)
    sd.append(st_dev)
    rgbs += colors
  # Export as excel
  df = pd.DataFrame([[a] + b + c + [d] for a, b, c, d in zip(concentrations, rgb, sd, [sum(triplet) / len(triplet) for triplet in sd])],
                    columns=['Lactate concentration (mM)', 'R (%)', 'G (%)', 'B (%)', 'SD of R', 'SD of G', 'SD of B', 'Average SD'])
  df.to_excel("excel/lactate concentration calibration curve.xlsx", index=False)
  df = pd.DataFrame([[a] + b for a, b in zip([element for element in concentrations for _ in range(3)], rgbs)],
                    columns=['Lactate concentration (mM)', 'R (%)', 'G (%)', 'B (%)'])
  df.to_excel("excel/raw data.xlsx", index=False)
  # Plots and errorbars of R
  red = np.array([i[0] for i in rgb])
  red_sd = [i[0] for i in sd]
  p1 = plt.plot(concentrations, red, color="lightcoral", marker="o")
  plt.errorbar(concentrations, red, red_sd, color="lightcoral", capsize=5)
  # Plots and errorbars of G
  green = np.array([i[1] for i in rgb])
  green_sd = [i[1] for i in sd]
  p2 = plt.plot(concentrations, green, color="yellowgreen", marker="D")
  plt.errorbar(concentrations, green, green_sd, color="yellowgreen", capsize=5)
  # Plots and errorbars of B
  blue = np.array([i[2] for i in rgb])
  blue_sd = [i[2] for i in sd]
  p3 = plt.plot(concentrations, blue, color="cornflowerblue", marker="s")
  plt.errorbar(concentrations, blue, blue_sd, color="cornflowerblue", capsize=5)
  # Add legends
  plt.legend((p1[0], p2[0], p3[0]), ("R", "G", "B"), loc='upper right')
  # Axis range
  plt.axis([-4, 54, 0, 100])
  plt.xlabel("Lactate concentration (mM)")
  plt.ylabel("Percentage of RGB color (%)")
  plt.show()

def main():
  images = []
  concentration_range = [0, 2, 4, 8, 16, 25, 50]
  for i in concentration_range:
    name = str(i)
    if len(str(i)) == 3:
      name = name + '0'
    images.append(load_images('calibration curve//' + name))
  comparison(images, concentration_range)


if __name__ == "__main__":
    main()
