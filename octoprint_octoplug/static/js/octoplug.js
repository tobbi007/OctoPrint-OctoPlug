$(function() {
    function OctoPlugViewModel(parameters) {
		var self = this;

		self.settingsViewModel = parameters[0];
		
		self.plugOn = function() {
			sendAPI("plugOn");
		};
		
		self.plugOff = function() {
			sendAPI("plugOff");
		};
		
		self.onBeforeBinding = function() {
			self.settings = self.settingsViewModel.settings;
		};
    }

	ADDITIONAL_VIEWMODELS.push([
		OctoPlugViewModel,
		["settingsViewModel"],
		["#settings_plugin_octoplug"]
	]);
	
	sendAPI = function(mycommand){
		$.ajax({
			url: API_BASEURL + "plugin/octoplug",
			type: "POST",
			dataType: "json",
			data: JSON.stringify({
				command: mycommand
			}),
			contentType: "application/json"
		})
	}
	
	testConfig = function(){
		sendAPI("plugOn");
		setTimeout(function(){sendAPI("plugOff")}, 3000);
	}
});




