## 
## HEAT_SOAK HEATER=<heater_name> TARGET=<target_heater_temperature> SOAKER=<heat_soak_temp_sensor_name> [RATE=<heat_soak_temp_rate_of_change>] [TIMEOUT=<time_to_abort_heat_soak>]
##
##
## e.g.
## HEAT_SOAK HEATER=heater_bed TARGET=100 SOAKER="temperature_sensor top_bed"
##
## Based on work by blalor: https://klipper.discourse.group/t/interruptible-heat-soak/1552
##

[gcode_macro HEAT_SOAK]
description: Wait for a temperature sensor to reach thermal equilibrium

variable_last_temp: 0
variable_last_soak_temp_rate: None
variable_temp_history: None
variable_smoothed_temp_history: None
variable_stage: "done" ## heating -> soaking -> done -> None
variable_total_time_elapsed: 0
variable_soak_time_remaining: 30
variable_check_interval: 1
variable_heating_report_interval: 2
variable_soaking_report_interval: 5
variable_heater_sensor: None
variable_soaker_sensor: None
variable_target_temp: 0.0
variable_min_soak_temp: 0
variable_target_rate: 0.3
variable_complete: None
variable_cancel: None
variable_temp_smooth_time: 4.0
variable_rate_smooth_time: 20.0
variable_resume_trigger: False
variable_was_print_active: False

gcode:
    { action_respond_info( "Heat Soak starting" )}

    # Soaker is required
    {% set SOAKER = params.SOAKER | string %}
    {% set RATE = params.RATE | default(0.3) | float %} ## in degrees C per minute
    {% set SOAK_TEMP = params.SOAK_TEMP | default(0.0) | float %}
    {% set HEATER = (params.HEATER | string) %} # Optional heater
    {% set TARGET = params.TARGET | default(0) | float %}
    {% set TIMEOUT = (params.TIMEOUT | default(30) | int) * 60 %} ## minutes to seconds
    {% set TEMP_SMOOTH = params.TEMP_SMOOTH | default(4.0) | float %} ## seconds for temp smoothing
    {% set RATE_SMOOTH = params.RATE_SMOOTH | default(20) | float %} ## seconds for rate smoothing
    {% set COMPLETE  = (params.COMPLETE | string) %}
    {% set CANCEL  = (params.CANCEL | string) %}
    {% set HEATING_REPORT_INTERVAL  = params.HEATING_REPORT_INTERVAL | default(2) | int %}
    {% set SOAKING_REPORT_INTERVAL  = params.SOAKING_REPORT_INTERVAL | default(5) | int %}

    # User writeable variables
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=heater_sensor           VALUE="{HEATER | pprint}"
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=target_temp             VALUE={TARGET}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=min_soak_temp           VALUE={SOAK_TEMP}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=soaker_sensor           VALUE="{SOAKER | pprint}"
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=target_rate             VALUE={RATE}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=soak_time_remaining     VALUE={TIMEOUT}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=complete                VALUE="'{COMPLETE}'"
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=cancel                  VALUE="'{CANCEL}'"
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=temp_smooth_time        VALUE={TEMP_SMOOTH}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=rate_smooth_time        VALUE={RATE_SMOOTH}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=heating_report_interval VALUE={HEATING_REPORT_INTERVAL}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=soaking_report_interval VALUE={SOAKING_REPORT_INTERVAL}

    # Internal variables
    {% set soak_temp = printer[SOAKER].temperature %}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=last_temp               VALUE={soak_temp}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=temp_history            VALUE="{[soak_temp] | pprint}"
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=smoothed_temp_history   VALUE="{[] | pprint}"
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=total_time_elapsed      VALUE=0
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=last_soak_temp_rate     VALUE=None
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=check_interval          VALUE=1.0
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=resume_trigger          VALUE=False
    {% set is_print_active = printer['virtual_sdcard'].is_active or printer['virtual_sdcard'].file_position != 0.0 %}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=was_print_active        VALUE={is_print_active}

    # start optional heater
    {% if (HEATER and TARGET != 0.0) %}
        SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=stage               VALUE="'heating'"
        SET_HEATER_TEMPERATURE HEATER={HEATER} TARGET={TARGET}
    {% else %}
        SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=stage               VALUE="'soaking'"
    {% endif %}

    # pause the print, if active
    {% if is_print_active %}
        PAUSE
    {% endif %}
    
    UPDATE_DELAYED_GCODE ID=_heat_soaker DURATION={check_interval}

[gcode_macro STOP_HEAT_SOAK]
description: stops heat soak activity without running any callbacks
gcode:
    UPDATE_DELAYED_GCODE ID=_heat_soaker DURATION=0  # cancel any pending run
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=stage VALUE="'done'"

[gcode_macro CANCEL_HEAT_SOAK]
description: cancels an in-progress HEAT_SOAK cycle and runs the cancel callback
gcode:
    # check that the HEAT_SOAK macro is active before canceling
    {% set heat_soak = printer['gcode_macro HEAT_SOAK'] %}
    {% set stage = heat_soak.stage %}
    {% if stage in ("heating", "soaking") %}
        STOP_HEAT_SOAK
        {% if heat_soak.cancel %}
            {heat_soak.cancel}
        {% endif %}
    {% endif %}

[gcode_macro HEAT_SOAK_RESUME]
description: Resume while heat soaking results in the soaking phase being skipped, any complete callback is run
gcode:
    {% set ON_RESUME = (params.ON_RESUME | default("_HEAT_SOAK__BASE_RESUME")) | string %}
    {% set heat_soak = printer['gcode_macro HEAT_SOAK'] %}
    {% set stage = heat_soak.stage %}
    {% if stage == "heating"  %}
        SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=resume_trigger VALUE=True
    {% elif stage == "soaking" %}
        STOP_HEAT_SOAK
        {% if heat_soak.complete %}
            {heat_soak.complete}
        {% endif %}
        {ON_RESUME} {% for p in params %}{'%s=%s ' % (p, params[p])}{% endfor %}
    {% else %}
        {ON_RESUME} {% for p in params %}{'%s=%s ' % (p, params[p])}{% endfor %}
    {% endif %}

[gcode_macro RESUME]
description: Resume while heat soaking results in the soaking phase being skipped, any complete callback is run
rename_existing: _HEAT_SOAK__BASE_RESUME
gcode:
    HEAT_SOAK_RESUME ON_RESUME=_HEAT_SOAK__BASE_RESUME

[delayed_gcode _heat_soaker]
# description: internal macro to handle heat soaking activity
gcode:
    {% set heat_soak = printer['gcode_macro HEAT_SOAK'] %}
    # debug
    #{ action_respond_info( printer['gcode_macro HEAT_SOAK'] | tojson )}

    # shut down cleanly if we detect that the user canceled or started a print while heat soaking
    {% set file_position_is_zero = (printer['virtual_sdcard'].file_position == 0.0 )%}
    {% if heat_soak.was_print_active and file_position_is_zero %}
        STOP_HEAT_SOAK
        {action_respond_info("HEAT_SOAK aborted. Detected a change in virtual_sdcard print state. Call STOP_HEAT_SOAK from CANCEL_PRINT to stop seeing this error message.")}
    {% endif %}

    # shut down cleanly if we detect that the user resumed the print while heat soaking
    {% if not file_position_is_zero and not printer['pause_resume'].is_paused %}
        STOP_HEAT_SOAK
        {action_respond_info("HEAT_SOAK aborted. Print is no longer paused. Call STOP_HEAT_SOAK or HEAT_SOAK_RESUME from your RESUME macro to stop seeing this error message.")}
    {% endif %}

    # update total time elapsed
    {% set total_time_elapsed = heat_soak.total_time_elapsed + heat_soak.check_interval %}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=total_time_elapsed VALUE={ total_time_elapsed }

    {% set soaker_sensor = printer[heat_soak.soaker_sensor] %}
    {% set soak_temp = soaker_sensor.temperature %}
    {% if heat_soak.heater_sensor %}
        {% set heater_sensor = printer[heat_soak.heater_sensor] %}
        {% set heater_temp = heater_sensor.temperature | round(1) %}
    {% endif %}
    {% set stage = heat_soak.stage %}

    # compute the new temp difference and save history
    {% set temp_history = heat_soak.temp_history %}
    {% set smoothed_temp_history = heat_soak.smoothed_temp_history %}
    {% set temp_diff = soak_temp - (temp_history | last) %}
    {% set _ = temp_history.append(soak_temp) %}
    {% set soak_temp_smoothed = None %}
    {% set slope = None %}
    {% if (temp_history | length) > heat_soak.temp_smooth_time %}
        {% set temp_history = temp_history[1:] %}
        # compute average temp
        {% set soak_temp_smoothed = ((temp_history | sum) / (temp_history | length)) %}
        # save raw value to history
        {% set _ = smoothed_temp_history.append(soak_temp_smoothed) %}
        # round off for display and comparisons later
        {% set soak_temp_smoothed = soak_temp_smoothed | round(3) %}
        # compute the slope
        {% if (smoothed_temp_history | length) > heat_soak.rate_smooth_time %}
            {% set smoothed_temp_history = smoothed_temp_history[1:] %}
            # Least Squares 
            # adapted from: https://towardsdatascience.com/linear-regression-using-least-squares-a4c3456e8570
            # X values are time in seconds
            # Y values are temperatures
            {% set count = (smoothed_temp_history | length) %}
            {% set times = range(0, count, 1) %}
            {% set x_sum = (times | sum) | float %}
            {% set y_sum = (smoothed_temp_history | sum) | float %}
            # Squares
            # Jinja oddity: += doesn't work in loops??, so collect squares and sum after
            {% set xx_sum_arr = [] %}
            {% set xy_sum_arr = [] %}
            {% for i in times %}
                {% set x = times[i] %}
                {% set y = smoothed_temp_history[i] %}
                {% set _ = xx_sum_arr.append(x * x) %}
                {% set _ = xy_sum_arr.append(x * y) %}
            {% endfor %}
            {% set xx_sum = (xx_sum_arr | sum) | float %}
            {% set xy_sum = (xy_sum_arr | sum) | float %}
            # Slope calculation. Slope is per second so * 60 for rate per minute
            {% set slope = (60.0 * ((count | float * xy_sum) - (x_sum * y_sum)) / ((count | float * xx_sum) - (x_sum * x_sum))) | round(3) %}
        {% endif %}
    {% endif %}
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=temp_history VALUE="{(temp_history | pprint | replace("\n", ""))}"
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=smoothed_temp_history VALUE="{(smoothed_temp_history | pprint | replace("\n", ""))}"

    # while heating
    {% if stage == "heating" %}
        {% if heater_temp < heat_soak.target_temp %}
            {% if total_time_elapsed % heat_soak.heating_report_interval == 0 %}
                {% set message = "Heating -- %.1fC / %.1fC -- %.1fm elapsed" % (heater_temp, heat_soak.target_temp, total_time_elapsed / 60.0) %}
                M117 {message}
                {action_respond_info(message)}
            {% endif %}
        {% else %}
            {action_respond_info("Heating completed after ~%.1fm, starting heat soak phase." % (total_time_elapsed / 60.0))}
            # skip the soak phase if resume was pressed
            {% set stage = "done" if heat_soak.resume_trigger else "soaking" %}
            # reset total time to 0 so soaking time is reported from 0
            {% set total_time_elapsed = 0 %}
            SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=total_time_elapsed VALUE={ total_time_elapsed }
        {% endif %}
    {% endif %}

    # while soaking
    {% if stage == "soaking" %}
        ## decrement the soak countdown
        {% set soak_time_remaining = [heat_soak.soak_time_remaining - heat_soak.check_interval, 0] | max %}
        SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=soak_time_remaining VALUE={ soak_time_remaining }

        ## abort soaking if timeout is reached
        {% if soak_time_remaining <= 0 %}
            {action_respond_info("Heat soak timed out after ~%.1fm" % (total_time_elapsed / 60.0))}
            {% set stage = "cancel" %}
        # if the smoothing algorithm hasn't settled on these values yet, dont evaluate them
        {% elif slope is none or soak_temp_smoothed is none %}
            {% if total_time_elapsed % heat_soak.soaking_report_interval == 0 %}
                ## not enough data points yet to determing the soak rate, show dashes
                {% set message = "Soaking -- gathering data -- %.1fm remaining" % (soak_time_remaining / 60.0) %}
                M117 { message }
                {action_respond_info(message)}
            {% endif %}
        # if the heat soak must continue for some reason
        {% elif (slope > heat_soak.target_rate) or (heat_soak.min_soak_temp > 0 and soak_temp_smoothed < heat_soak.min_soak_temp) %}
            {% if total_time_elapsed % heat_soak.soaking_report_interval == 0 %}
                {% set format_vars = [
                    soak_temp_smoothed | float,
                    (heat_soak.min_soak_temp | float | round(0) | string) if (heat_soak.min_soak_temp > 0) else "--",
                    slope,
                    heat_soak.target_rate,
                    soak_time_remaining / 60.0
                ] %}
                {% set message = "Soaking -- temp: {0:.1f}C / {1}C -- rate: {2:.3f}C/m / {3:.3f}C/m -- {4:.1f}m remaining".format(*format_vars) %}
                M117 { message }
                {action_respond_info(message)}
            {% endif %}
        ## end soaking if the target rate is achieved
        {% else %}
            {action_respond_info("Heat soak complete after ~%.1fm at %.3fC/m / %.1fC" % (total_time_elapsed / 60.0, slope, soak_temp))}
            {% set stage = "done" %}
        {% endif %}
    {% endif %}

    # save stage before calling any macros
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=stage VALUE="'{stage}'"

    {% if stage in ("done", "cancel") %}
        STOP_HEAT_SOAK
        {% if stage == "cancel" %}
            {% if heat_soak.cancel %}
                {heat_soak.cancel}
            {% elif printer['virtual_sdcard'].is_active %}
                CANCEL_PRINT
            {% endif %}
        {% else %}
            {% if heat_soak.complete %}
                {heat_soak.complete}
            {% endif %}
            {% if printer['pause_resume'].is_paused  %}
                RESUME
            {% endif %}
        {% endif %}
    {% else %}
        ## trigger ourselves again
        UPDATE_DELAYED_GCODE ID=_heat_soaker DURATION={ heat_soak.check_interval }
        ## dwell for 1ms to prevent from going idle
        G4 P1
    {% endif %}

    # save ending value of stage
    SET_GCODE_VARIABLE MACRO=HEAT_SOAK VARIABLE=stage VALUE="'{stage}'"