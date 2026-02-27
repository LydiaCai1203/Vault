import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Router, Route, Switch } from "wouter";
import { useHashLocation } from "wouter/use-hash-location";
import ErrorBoundary from "@/components/ErrorBoundary";
import { ThemeProvider } from "@/contexts/ThemeContext";

import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Trades from "@/pages/Trades";
import TradeDetail from "@/pages/TradeDetail";
import RecordTrade from "@/pages/RecordTrade";
import Reviews from "@/pages/Reviews";
import ReviewDetail from "@/pages/ReviewDetail";
import Checklist from "@/pages/Checklist";
import Profile from "@/pages/Profile";
import NotFound from "@/pages/NotFound";

function AppRouter() {
  return (
    <Router hook={useHashLocation}>
      <Switch>
        <Route path="/login" component={Login} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/trades" component={Trades} />
        <Route path="/trades/:id">{(p) => <TradeDetail id={p.id} />}</Route>
        <Route path="/record" component={RecordTrade} />
        <Route path="/reviews" component={Reviews} />
        <Route path="/reviews/:id">{(p) => <ReviewDetail id={p.id} />}</Route>
        <Route path="/checklist" component={Checklist} />
        <Route path="/profile" component={Profile} />
        <Route path="/" component={Dashboard} />
        <Route component={NotFound} />
      </Switch>
    </Router>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <TooltipProvider>
          <Toaster />
          <AppRouter />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
