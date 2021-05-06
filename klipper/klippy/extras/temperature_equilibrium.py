import logging

class TemperatureEquilibrium:
    def __init__(self, config):
        self.printer = config.get_printer()
        # Register commands
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command("TEMPERATURE_EQUILIBRIUM", self.cmd_TEMPERATURE_EQUILIBRIUM,
                               desc=self.cmd_TEMPERATURE_EQUILIBRIUM_help)

    def _tempRateLeastSquares(self, temp_values):
        x_sum = 0
        y_sum = 0
        xy_sum = 0
        x_squared_sum = 0
        n = len(temp_values)

        # sums
        for i in range(n):
            x = temp_values[i][0]
            y = temp_values[i][1]
            x_sum += x
            y_sum += y
            xy_sum += (x * y)
            x_squared_sum += (x * x)

        # Calculate m for the line equation y = (m * x) + b
        # this is the slope of the line which represents the rate of change of the temprature in degrees/second
        return abs((xy_sum - x_sum * y_sum / n) / (x_squared_sum - x_sum * x_sum / n))

    cmd_TEMPERATURE_EQUILIBRIUM_help = "Wait for a temperature on a sensor to reach thermal equilibrium"

    def cmd_TEMPERATURE_EQUILIBRIUM(self, gcmd):
        sensor_name = gcmd.get('SENSOR')
        heaters = self.printer.lookup_object('heaters')
        sensors = heaters.available_sensors
        # your selected sensor must exist
        if sensor_name not in sensors:
            raise gcmd.error("Unknown sensor '%s'" % (sensor_name,))
        # TODO: if the sensor is attached to a heater, throw an error. This is for non-heater driven temp sensors.
        sensor = self.printer.lookup_object(sensor_name)
        # The default rate is 0.5 degrees of change per minute, the minimum is 0.1
        target_temp_rate_per_minute = gcmd.get_float('CHANGE_PER_MINUTE', default = 0.5, minval = 0.1)
        min_data_points = 5      # To speed up "hot" print starts this algorithm only waits 5s before trying to compute a rate
        # Adjusting the WINDOW parameter changes how sensitive the algorithm is to noise in the sensor reading. 
        # If you are trying for a very small CHANGE_PER_MINUTE value, using a large WINDOW can help make this more stable
        window_size = gcmd.get_float('WINDOW', default = 30, minval = min_data_points, maxval = 60)

        # if debugging, quit
        if self.printer.get_start_args().get('debugoutput') is not None:
            return
        
        temp_data = []
        reactor = self.printer.get_reactor()
        start_time = reactor.monotonic()
        eventtime = start_time
        while not self.printer.is_shutdown():
            temp, target = sensor.get_temp(eventtime)
            temp_data.append((eventtime, temp))
            if len(temp_data) > window_size:
                temp_data.pop(0)

            rate_per_minute = "..."
            if len(temp_data) >= min_data_points:
                rate_per_minute = round(self._tempRateLeastSquares(temp_data) * 60, 1)
                if rate_per_minute < target_temp_rate_per_minute:
                    time_taken = round(eventtime - start_time, 0)
                    gcmd.respond_raw('Temperature equilibrium reached in {0}s at {1}C '.format(time_taken, round(temp, 1)))
                    return
            gcmd.respond_raw('{0}C:{1}C/s /{2}C/s'.format(round(temp, 1), rate_per_minute, target_temp_rate_per_minute))
            eventtime = reactor.pause(eventtime + 1.)

def load_config(config):
    return TemperatureEquilibrium(config)
