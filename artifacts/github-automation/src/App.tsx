import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Layout } from "@/components/Layout";

import Dashboard from "@/pages/Dashboard";
import Automations from "@/pages/Automations";
import NewAutomation from "@/pages/NewAutomation";
import AutomationDetail from "@/pages/AutomationDetail";
import Runs from "@/pages/Runs";
import WebhookEvents from "@/pages/WebhookEvents";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/automations" component={Automations} />
        <Route path="/automations/new" component={NewAutomation} />
        <Route path="/automations/:id" component={AutomationDetail} />
        <Route path="/runs" component={Runs} />
        <Route path="/webhook-events" component={WebhookEvents} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  // Force dark mode on body
  document.documentElement.classList.add("dark");

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
