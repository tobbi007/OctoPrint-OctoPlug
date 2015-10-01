# coding=utf-8
from __future__ import absolute_import
from . import smartplug

import octoprint.plugin
import octoprint.events

class OctoPlugPlugin(  octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
					   octoprint.plugin.SimpleApiPlugin,
					   octoprint.plugin.EventHandlerPlugin):
					   
	
	def on_after_startup(self):
		self._logger.info("OctoPlugPlugin started!")
		self.currentlayer = 0
		self.printing = False
		self.ediplug = smartplug.SmartPlug(self._settings.get(["ip"]), self._settings.get(["port"]), (self._settings.get(["usr"]),self._settings.get(["pwd"])))

	def get_settings_defaults(self):
		return dict(
			ip=None,
			port=None,
			usr=None,
			pwd=None,
			reactgcode=True,
			layer="3"
		)

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	def get_assets(self):
		return dict(
			js=["js/octoplug.js"]
		)
	
	def get_api_commands(self):
		return dict(
			plugOn=[],
			plugOff=[]
		)
	
	def on_api_command(self, command, data):
		if command == "plugOn":
			self.ediplug.state = "ON"
		elif command == "plugOff":
			self.ediplug.state = "OFF"
				
	def gcodeFanHook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if self._settings.get(["reactgcode"]):
			if gcode == "M106" and "S0" not in cmd:
				self.ediplug.state = "ON"
			elif (gcode == "M106" and "S0" in cmd) or gcode == "M107":
				self.ediplug.state = "OFF"
	
	def on_event(self, event, payload):	
		if event == octoprint.events.Events.PRINT_STARTED:
			self.currentlayer = 0
			self.printing = True
			
		elif event == "ZChange":
			if self.printing == True:
				self.currentlayer += 1
				if str(self.currentlayer) == str(self._settings.get(["layer"])):
					self.ediplug.state = "ON"
					
		elif event == "PrintFailed" or event == "PrintDone" or event == "PrintCancelled" or event == "PrintPaused":
			self.ediplug.state = "OFF"
			self.printing = False
			
		elif event == "PrintResumed" and self.currentlayer > self._settings.get(["layer"]):
			self.ediplug.state = "ON"
			self.printing = True
			
		elif event == "SettingsUpdated":
			self.ediplug = smartplug.SmartPlug(self._settings.get(["ip"]), self._settings.get(["port"]), (self._settings.get(["usr"]),self._settings.get(["pwd"])))

		
__plugin_name__ = "OctoPlug"
__plugin_implementation__ = OctoPlugPlugin()
__plugin_hooks__ = {"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.gcodeFanHook}
