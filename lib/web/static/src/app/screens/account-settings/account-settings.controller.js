export function AccountSettingsController(AppApi, $stateParams,$mdDialog , $mdToast, $state) {
  console.log($stateParams.accountId)
    var $ctrl = this;
	$ctrl.api_key;
	$ctrl.team_url;
	$ctrl.$mdToast = $mdToast;
    $ctrl.integration_id = $stateParams.accountId
    $ctrl.submitForm = function(){
//        $ctrl.isDisabled = true;
//        console.log($ctrl.accountDetails.AWS_APIAccessKey)
//                                console.log($ctrl.accountDetails.AWS_APISecretAccess)
//                                console.log($ctrl.integration_id)
//                                console.log("aasdfghjkzxcvbnm")

		AppApi.submitForm({
//
		                        'BOX_ACCESS_TOKEN': $ctrl.accountDetails.BOX_ACCESS_TOKEN,
                                'BOX_REFRESH_TOKEN': $ctrl.accountDetails.BOX_REFRESH_TOKEN,
                                //'AGILE_DOMAIN_NAME' :  $ctrl.accountDetails.AGILE_DOMAIN_NAME,
//                                'AZURE_client_secret' : $ctrl.accountDetails.AZURE_client_secret,
//                                'user_integration_id': $stateParams.accountId,
                                'BOX_UPDATE_LOGIN_FLAG' : $ctrl.accountDetails.BOX_UPDATE_LOGIN_FLAG,
                                'YELLOWANT_INVOKE_NAME':$ctrl.accountDetails.YELLOWANT_INVOKE_NAME,
                                'user_integration':$stateParams.accountId,


									})
									.then(function(response){
									if(response.status==200){
									    console.log("hello ")
									    $ctrl.showSimpleToast(response.data);
									    $ctrl.isDisabled = false;}
	                                else{
	                                    $ctrl.returned = "Something went wrong, try again later";
	                                    $ctrl.isDisabled = false;
	                                    }
	                                 });
	}

//	$ctrl.submitSettings = function(){
//	    AppApi.submitSettings({
//	                            'new_ticket_notification': $ctrl.accountDetails.notification,
//	                            'integration_id': $ctrl.integration_id,}).then(function(response){
//									if(response.status==200){
//									    $ctrl.showSimpleToast(response.data);
//									    }
//	                                else{
//	                                    $ctrl.returned = "Something went wrong, try again later";
//
//	                                    }
//	                                 });
//	}

    $ctrl.goBack = function(){
        $state.go('accountList')
    }

    $ctrl.newUrl = function(){
        AppApi.newUrl({'integration_id':$ctrl.integration_id})
            .then(function(result){
//                console.log(result)
                $ctrl.accountDetails.callback = result.data.callback;
            });
    }

    $ctrl.$onInit = function() {
        AppApi.getUserAccount($stateParams.accountId)
        .then(function (result) {
            $ctrl.userAccounts = result.data;
           console.log($ctrl.userAccounts.is_valid);
        });
      }

    $ctrl.deleteaccount = function() {

        console.log("Deleting")

        AppApi.deleteUserAccount($stateParams.accountId).then(function() {
            $mdToast.show($ctrl.$mdToast.simple().textContent("Deleted Account").hideDelay(10000));
            $state.go('accountList');
        },
        function (error) {
            $mdToast.show($ctrl.$mdToast.simple().textContent("Failed").hideDelay(10000))
        });
    };




  $ctrl.showSimpleToast = function(data) {
    console.log("Inside toast")
    $mdToast.show(
                     $ctrl.$mdToast.simple()
                        .textContent("Successful")
                        .hideDelay(10000)
                  )};

                  $ctrl.showConfirm = function(ev) {
  var confirm = $mdDialog.confirm()
        .title('Are you sure you want to delete this account?')
        .textContent('Deleting this account will erase all data asscosciated with it!')
        .ariaLabel('Delete Account')
        .targetEvent(ev)
        .ok("Delete")
        .cancel("Cancel");
  $mdDialog.show(confirm).then(function() {
    $ctrl.status = 'We are deleting your account.';

    AppApi.deleteUserAccount($stateParams.accountId)
    $state.go('accountList');
    });
}

}


