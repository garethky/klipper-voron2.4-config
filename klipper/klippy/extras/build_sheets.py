# build sheets module stores a "Live-Z" value for each toolhead/sheet combination you have
import logging, json, os.path as path

class BuildSheetManager:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()
        klipper_config_file = self.printer.get_start_args()['config_file']
        self.build_sheets_config_file = \
            klipper_config_file[:klipper_config_file.rindex("/")] + self.BUILD_SHEET_FILE
        self.build_sheets_data = self._load_build_sheets()
        self.current_tool = None
        self.is_toolchanger = config.getboolean('is_toolchanger', False)
        self.override_get_gcode_offset = config.getboolean('override_set_gcode_offset', True)
        self.gcode_move = self.printer.load_object(config, 'gcode_move')
        self.gcode = self.printer.lookup_object('gcode')
        self._register_commands()

    BUILD_SHEET_FILE = "/build_sheets.json"
    SHEETS_KEY = "BuildSheets"
    LIVE_Z_KEY = "LiveZ"
    INSTALLED_SHEET_KEY = "InstalledSheet"

    def _register_commands(self):
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command("BUILD_SHEETS_STATUS", self.cmd_BuildSheetsStatus,
                               desc=self.cmd_BuildSheetsStatus_help)
        gcode.register_command("ADD_BUILD_SHEET", self.cmd_AddSheet,
                               desc=self.cmd_AddSheet_help)
        gcode.register_command("DELETE_BUILD_SHEET", self.cmd_DeleteSheet,
                               desc=self.cmd_DeleteSheet_help)
        gcode.register_command("INSTALL_BUILD_SHEET", self.cmd_InstallSheet,
                               desc=self.cmd_InstallSheet_help)
        gcode.register_command("REMOVE_BUILD_SHEET", self.cmd_RemoveSheet,
                               desc=self.cmd_RemoveSheet_help)
        gcode.register_command("SET_BUILD_SHEET_TOOL", self.cmd_SelectTool,
                               desc=self.cmd_SelectTool_help)
        gcode.register_command("SET_BUILD_SHEET_LIVE_Z", self.cmd_SetLiveZ,
                               desc=self.cmd_SetLiveZ_help)
        if self.override_get_gcode_offset:
            base_get_gcode_offset = gcode.register_command("SET_GCODE_OFFSET", None)
            gcode.register_command("BASE_SET_GCODE_OFFSET", base_get_gcode_offset)
            gcode.register_command("SET_GCODE_OFFSET", self.cmd_SetGCodeOffsetOverride,
                               desc=self.cmd_SetGCodeOffsetOverride_help)

    def installed_sheet_name(self):
        return self.build_sheets_data[self.INSTALLED_SHEET_KEY]

    def sheets(self):
        return self.build_sheets_data[self.SHEETS_KEY]
    
    def installed_sheet(self):
        if not self.sheet_exists(self.installed_sheet_name()):
            return None
        return self.sheets()[self.installed_sheet_name()]

    def sheet_exists(self, sheet_name):
        return sheet_name and sheet_name in self.sheets()

    def _get_tool_key(self):
        return self.current_tool if self.is_toolchanger else self.LIVE_Z_KEY

    def _is_z_homed(self):
        toolhead = self.printer.lookup_object('toolhead')
        curtime = self.printer.get_reactor().monotonic()
        return 1 if 'z' in toolhead.get_status(curtime)['homed_axes'] else 0

    def get_live_z_offset(self):
        offset = 0.0
        tool_key = self._get_tool_key()
        installed_sheet = self.installed_sheet()
        if installed_sheet:
            if tool_key in installed_sheet:
                offset = installed_sheet[tool_key]
        return offset

    def update_live_z(self):
        params = {"Z": self.get_live_z_offset(), "MOVE": self._is_z_homed()}
        z_offset_command = self.gcode.create_gcode_command("SET_GCODE_OFFSET", "SET_GCODE_OFFSET", params)
        self.gcode_move.cmd_SET_GCODE_OFFSET(z_offset_command)

    def _load_build_sheets(self):
        # create config file if missing
        if not path.exists(self.build_sheets_config_file):
            self.build_sheets_data = {self.INSTALLED_SHEET_KEY: None, self.SHEETS_KEY: {}}
            self._save_build_sheets()

        with open(self.build_sheets_config_file) as infile:
            return json.load(infile)
        
    def _save_build_sheets(self):
        with open(self.build_sheets_config_file, 'w') as outfile:
            json.dump(self.build_sheets_data, outfile)

    cmd_BuildSheetsStatus_help = "List all build sheets and current build sheet system status"
    def cmd_BuildSheetsStatus(self, gcmd):
        strBuilder = []
        installedSheet = self.installed_sheet()
        strBuilder.append("Installed Build Sheet: {0}\n".format(self.installed_sheet_name()))
        if self.is_toolchanger:
            strBuilder.append("Current Tool: {0}\n".format(self.current_tool))
        strBuilder.append("Current Live Z Offset: {0}\n".format(self.get_live_z_offset()))
        strBuilder.append("Available Build Sheets:\n")
        for sheet_name in self.sheets():
            sheet = self.sheets()[sheet_name]
            prefix = "> " if sheet_name == installedSheet else "* "
            strBuilder.append("{0}{1}: ".format(prefix, sheet_name))
            sheetOffsets = []
            for tool_key in sheet:
                offsetPrefix = "(*) " if tool_key == self.current_tool else ""
                sheetOffsets.append("{0}{1}: {2}".format(offsetPrefix, tool_key, sheet[tool_key]))
            strBuilder.append(', '.join(sheetOffsets))
            strBuilder.append('\n')
        gcmd.respond_raw(''.join(strBuilder))

    cmd_AddSheet_help = "Create a new build sheet"
    def cmd_AddSheet(self, gcmd):
        sheet_name = gcmd.get('SHEET')
        if self.sheet_exists(sheet_name):
            gcmd.error("A build sheet named '{0}' already exists".format(sheet_name))
            return
        
        self.sheets()[sheet_name] = {}
        self._save_build_sheets()

    cmd_DeleteSheet_help = "Delete an existing build sheet"
    def cmd_DeleteSheet(self, gcmd):
        sheet_name = gcmd.get('SHEET')
        if not self.sheet_exists(sheet_name):
            gcmd.error("Unknown build sheet '{0}'".format(sheet_name))
            return
        
        del self.sheets()[sheet_name]
        # if that sheet was installed, remove it:
        if self.installed_sheet_name() == sheet_name:
              self.build_sheets_data[self.INSTALLED_SHEET_KEY] = None
        self._save_build_sheets()
        self.update_live_z()

    cmd_InstallSheet_help = "Install a build sheet into the printer"
    def cmd_InstallSheet(self, gcmd):
        sheet_name = gcmd.get('SHEET')
        if not self.sheet_exists(sheet_name):
            gcmd.error("Unknown build sheet '{0}'".format(sheet_name))
            return

        self.build_sheets_data[self.INSTALLED_SHEET_KEY] = sheet_name
        self._save_build_sheets()
        self.update_live_z()
    
    cmd_RemoveSheet_help = "Remove the currently installed build sheet from the printer"
    def cmd_RemoveSheet(self, gcmd):
        self.build_sheets_data[self.INSTALLED_SHEET_KEY] = None
        self._save_build_sheets()
        self.update_live_z()

    cmd_SelectTool_help = "Set the current tool"
    def cmd_SelectTool(self, gcmd):
        if not self.is_toolchanger:
            gcmd.error("Not configured to use tools. Use 'is_toolchanger: True' to configure tool use.")

        tool_name = gcmd.get('TOOL', None)
        # allow empty string, "None" or "False" to select no tool
        if tool_name is not None and (not tool_name.strip() or tool_name.lower() == "none" or tool_name.lower() == "false" ):
            tool_name = None
        self.current_tool = tool_name
        self.update_live_z()

    cmd_SetLiveZ_help = "Set the build sheet live Z value"
    def cmd_SetLiveZ(self, gcmd):
        z_offset = gcmd.get_float('Z', default = None)
        z_adjust = gcmd.get_float('Z_ADJUST', default = None)
        sheet_name = gcmd.get('SHEET', default = None)
        tool = self._get_tool_key()

        if sheet_name:
            if not self.sheet_exists(sheet_name):
                gcmd.error("Unknown build sheet '{0}'".format(sheet_name))
                return
            sheet = self.sheets()[sheet_name]
        elif self.installed_sheet() is None:
            gcmd.error("No build sheet installed")
            return
        else:
            sheet = self.installed_sheet()
        
        # note the 'None' checks here are important because 0.0 is falsey
        if z_offset is not None:
            sheet[tool] = z_offset
        elif z_adjust is not None:
            # add tool key if missing, initalize to 0.0
            if not tool in sheet:
                sheet[tool] = 0.0
            sheet[tool] += z_adjust
        else:
            gcmd.error("No Z or Z_ADJUST parameter provided, one is required")

        self._save_build_sheets()
        self.update_live_z()

    cmd_SetGCodeOffsetOverride_help = "Set the GCode Offset. Z is controlled by build sheet offset."
    def cmd_SetGCodeOffsetOverride(self, gcmd):
        # copy all params
        params = gcmd.get_command_parameters()

        z_offset = gcmd.get_float('Z', default = None)
        z_adjust = gcmd.get_float('Z_ADJUST', default = None)
        has_z_adjustment = z_offset is not None or z_adjust is not None
        sheet = self.installed_sheet()

        # in the case of a tool changer you must have a tool selected to adjust live Z
        if sheet and has_z_adjustment and self.is_toolchanger and not self.current_tool:
            gcmd.error("No tool is selected for Live Z adjustment")

        # only apply Z to the sheet model if a sheet is installed and a Z adjustment was requested
        # all other cases are pass through
        if sheet and has_z_adjustment:
            tool = self._get_tool_key()
            if z_offset is not None:
                sheet[tool] = z_offset
            elif z_adjust is not None:
                # add tool key if missing, initalize to 0.0
                if not tool in sheet:
                    sheet[tool] = 0.0
                sheet[tool] += z_adjust
            # override the supplied argument with the one from the build sheet model
            del params['Z_ADJUST'] 
            params['Z']= self.get_live_z_offset()
        # TODO: in the case where no sheet is installed, what is the right behaviour here?
        # currently any changes will be lost when a sheet is installed, personally im OK with this but
        # maybe not everyone will be

        offset_command = self.gcode.create_gcode_command("BASE_SET_GCODE_OFFSET", "BASE_SET_GCODE_OFFSET", params)
        self.gcode_move.cmd_SET_GCODE_OFFSET(offset_command)

def load_config(config):
    return BuildSheetManager(config)
