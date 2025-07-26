import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AnimalManagementPage from './pages/AnimalManagementPage';
import ScoringPage from './pages/ScoringPage';
import DashboardPage from './pages/DashboardPage';
import NotFoundPage from './pages/NotFoundPage';

const App: React.FC = () => {
    return (
        <Router>
            <Switch>
                <Route path="/" exact component={HomePage} />
                <Route path="/animals" component={AnimalManagementPage} />
                <Route path="/scoring" component={ScoringPage} />
                <Route path="/dashboard" component={DashboardPage} />
                <Route component={NotFoundPage} />
            </Switch>
        </Router>
    );
};

export default App;