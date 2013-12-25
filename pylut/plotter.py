class LUTPlotter:

  @staticmethod
  def Plot(lut):
    """
    Plot a LUT as a 3D RGB cube using matplotlib. Stolen from https://github.com/mikrosimage/ColorPipe-tools/tree/master/plotThatLut.
    """

    try:
      import matplotlib
      # matplotlib : general plot
      from matplotlib.pyplot import title, figure
      # matplotlib : for 3D plot
      # mplot3d has to be imported for 3d projection
      import mpl_toolkits.mplot3d
      from matplotlib.colors import rgb2hex
    except ImportError:
      print "matplotlib not installed. Run: pip install matplotlib"
      return

    #for performance reasons lattice size must be 9 or less
    if lut.cubeSize > 9:
      lut = lut.Resize(9)

    # init vars
    cubeSize = lut.cubeSize
    input_range = xrange(0, cubeSize)
    max_value = cubeSize - 1.0
    red_values = []
    green_values = []
    blue_values = []
    colors = []
    # process color values
    for r in input_range:
      for g in input_range:
        for b in input_range:
          # get a value between [0..1]
          norm_r = r/max_value
          norm_g = g/max_value
          norm_b = b/max_value
          # apply correction
          res = lut.ColorFromColor(Color(norm_r, norm_g, norm_b))
          # append values
          red_values.append(res.r)
          green_values.append(res.g)
          blue_values.append(res.b)
          # append corresponding color
          colors.append(rgb2hex([norm_r, norm_g, norm_b]))
    # init plot
    fig = figure()
    fig.canvas.set_window_title('pylut Plotter')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    ax.set_xlim(min(red_values), max(red_values))
    ax.set_ylim(min(green_values), max(green_values))
    ax.set_zlim(min(blue_values), max(blue_values))
    title(lut.name)
    # plot 3D values
    ax.scatter(red_values, green_values, blue_values, c=colors, marker="o")
    matplotlib.pyplot.show()
