import template from './account-list.html';
import { AccountListController as controller } from './account-list.controller';
import './account-list.scss';

controller.$inject = ['AppApi'];

export let AccountListScreen = {
  template,
  controller
};