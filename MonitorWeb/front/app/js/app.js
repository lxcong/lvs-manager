'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers','ui.bootstrap']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/agent', {templateUrl: 'agent.html', controller: Agent});
    $routeProvider.when('/view2', {templateUrl: 'partials/partial2.html', controller: 'MyCtrl2'});
    $routeProvider.otherwise({redirectTo: 'agent'});
  }]);

function Agent($scope) {
	$scope.isCollapsed = false;
} 

function NavbarCtlr() {
	
}