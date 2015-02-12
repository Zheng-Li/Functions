<?php
    /*
     *Show job details classified by the job itself
     */
	function organization_manager_jobs() {	
		$header = array(
			array('data' => 'ID', 'field' => 'id'),
			array('data' => 'Title', 'field' => 'title'),
            array('data' => 'Snippet', 'field' => 'snippet'),
			array('data' => 'Url', 'field' => 'url'),
            array('data' => 'Url Status', 'field' => 'url_status'),
            array('data' => 'Organization', 'field' => 'org_name'),
			array('data' => 'City', 'field' => 'city'),
			array('data' => 'District', 'field' => 'district'),
			array('data' => 'Country', 'field' => 'country'),
			array('data' => 'Created On', 'field' => 'date_created'),
			array('data' => 'Expired On', 'field' => 'date_expired'),
            array('data' => 'Counter 1', 'field' => 'counter_1'),
            array('data' => 'Counter 2', 'field' => 'counter_2'), 
			array('data' => t('Operations'), 'colspan' => 2),
		);

		$query = db_select('zd_dev_jobs', 'j');
        $query -> join('zd_dev_organizations', 'o', 'j.Org_id = o.ID');
		$query -> join('zd_dev_location_city', 'c', 'j.City_id = c.ID');
        $query -> join('zd_dev_location_district', 'd', 'j.District_id = d.ID');
        $query -> join('zd_dev_location_country', 't', 'j.Country_id = t.ID');
		$query -> fields('j', array('ID', 'Title', 'Snippet', 'Url', 'Url_status'));
		$query -> fields('o', array('Name'));
        $query -> fields('c', array('Name'));
        $query -> fields('d', array('Name'));
        $query -> fields('t', array('Name'));
		$query -> fields('j', array('Created_on', 'Expired_on','Counter_1', 'Counter_2'));

		$query = $query
			->extend('TableSort')
			->orderByHeader($header)
			->extend('PagerDefault')
			->limit(10);
		$result = $query->execute();

		$rows = array();
		foreach ($result as $item) {
			$rows[] = array(
				$item->ID,
				$item->Title,
                strlen($item->Snippet) > 50 ? substr($item->Snippet,0,40)."..." : $item->Snippet,
				strlen($item->Url) > 35 ? substr($item->Url,0,28)."..." : $item->Url,
				$item->Url_status,
				$item->Name,
				$item->c_Name,
				$item->d_Name,
                $item->t_Name,
				$item->Created_on,
				$item->Expired_on,
                $item->Counter_1,
                $item->Counter_2,
				l(t('Edit'), 'admin/organization-manager/jobs/edit/'. $item->ID,array('query' => drupal_get_destination())),
				l(t('Delete Flag'), ''),
			);
		}

		$form['pager_top'] = array(
			'#theme' => 'pager',
			'#weight' => 1,
		);

		$form['job_urls'] = array(
			'#theme' => 'table',
			'#header' => $header,
			'#rows' => $rows,
			'#weight' => 2,
		);

		$form['pager_bottom'] = array(
			'#theme' => 'pager',
			'#weight' => 3,
		);

		// $form['actions']           = array('#type' => 'actions');
		// $form['actions']['submit'] = array('#type'  => 'submit', '#value' => t('Save Changes'));
		return $form;
	}

    // /*
    //  * Add new job by choosing existing organization or adding a new organization
    //  */
    // function organization_manager_jobs_add() {
    //     drupal_add_css(drupal_get_path('module', 'organization_manager') . '/css/select2.css');
    //     drupal_add_css(drupal_get_path('module', 'organization_manager') . '/css/organization_manager.css');

    //     drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/select2.min.js');
    //     drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/underscore-min.js');
    //     drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/backbone-min.js');
    //     drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/organization_manager.js');

    //     $var = array();
    //     return theme('organization_manager_add_job', $var);
    // }

    /*
     * Job editing page with pre-defined organization
     */
	function organization_manager_jobs_edit($id = 0) {
		if (isset($_POST['op'])) {
        	organization_manager_job_edit_submit($_POST);
    	}

   		drupal_add_css(drupal_get_path('module', 'organization_manager') . '/css/select2.css');
    	drupal_add_css(drupal_get_path('module', 'organization_manager') . '/css/organization_manager.css');

    	drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/select2.min.js');
    	drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/underscore-min.js');
    	drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/backbone-min.js');
    	drupal_add_js(drupal_get_path('module', 'organization_manager') . '/js/organization_manager.js');

    	$job = new stdClass();
    	$job->org_id 		   = 0;
    	$job->org_name         = '';
    	$job->org_url          = '';
        $job->org_tags         = '';
    	$job->job_id 		   = 0;
    	$job->job_title 	   = '';
        $job->job_snippet      = '';
        $job->job_url          = '';
        $job->job_url_status   = 200;
        $job->date_created     = '';
        $job->date_expired     = '';
        $job->city             = '';
        $job->district         = '';
        $job->country          = '';
        $job->weight           = 0;
    	$job->job_tags 		   = '';
    	
    	if($id) {
            $job_query = db_select('zd_dev_jobs', 'j');
            $job_query -> join('zd_dev_jobs_tags', 't', 'j.ID = t.ID');
            $job_query -> join('zd_dev_location_city', 'c', 'j.City_id = c.ID');
            $job_query -> join('zd_dev_location_district', 'd', 'j.District_id = d.ID');
            $job_query -> join('zd_dev_location_country', 'cc', 'j.Country_id = cc.ID');
            $job_query -> fields('j', array('ID', 'Title', 'Url', 'Url_status', 'Org_id', 'Job_weight', 'Created_on', 'Expired_on', 'Snippet'));
            $job_query -> fields('t', array('Tag'));
            $job_query -> fields('c', array('Name'));
            $job_query -> fields('d', array('Name'));
            $job_query -> fields('cc', array('Name'));
            $job_query -> condition('j.ID', $id);
            $job_result = $job_query -> execute();

            foreach($job_result as $item) {
                $job->job_id = $item->ID;
                $job->job_title = $item->Title;
                $job->job_tags = '';
                $job->job_url = $item->Url;
                $job->job_url_status = $item->Url_status;
                $job->org_id = $item->Org_id;
                $job->job_snippet = $item->Snippet;
                $job->weight = $item->Job_weight;
                $job->date_created = $item->Created_on;
                $job->date_expired = $item->Expired_on;
                $job->city = $item->Name;
                $job->district = $item->d_Name;
                $job->country = $item->cc_Name;
            }

            var_dump($job->org_id);
            $org_query = db_select('zd_dev_organizations', 'o');
            $org_query -> join('zd_dev_organizations_tags', 't', 'o.ID = t.ID');
            $org_query -> fields('o', array('ID', 'Name', 'Url'));
            $org_query -> fields('t', array('Tag'));
            $org_query -> condition('o.ID', $job->org_id);
            $org_result = $org_query -> execute();

            foreach ($org_result as $item) {
                $job->org_name = $item->Name;
                $job->org_url = $item->Url;
                $job->org_tags = '';
            }
    	}

    	$variables = array(
    		'org_id' 		=> $job->org_id,
    		'org_name' 		=> $job->org_name,
    		'org_url' 		=> $job->org_url,
            'org_tags'      => $job->org_tags,
    		'job_id' 		=> $job->job_id,
    		'job_title' 	=> $job->job_title,
    		'job_tags' 		=> $job->job_tags,
    		'job_url' 		=> $job->job_url,
            'job_url_status'=> $job->job_url_status,
    		'job_snippet' 	=> $job->job_snippet,
    		'date_created'	=> $job->date_created,
    		'date_expired' 	=> $job->date_expired,
            'weight'        => $job->weight,
    		'city' 			=> $job->city,
    		'district' 		=> $job->district,
    		'country' 		=> $job->country,
    		);

    	return theme('organization_manager_edit_job', $variables);
	}

    /*
     * Adding or Editing job with pre-defined organization
     */
	function organization_manager_job_edit_submit($var) {  
        $org_fields = array(
            'org_id'        => $var['org-id'],
            'org_name'      => $var['org-name'],
            'org_url'       => $var['org-url'],
            'org_tags'      => $var['org-tags'],
            );

        //Test
		$job_fields = array(
            'org_id'        => $var['org-id'],
            'job_id'        => $var['job-id'],
            'job_title'     => $var['job-title'],
            'job_tags'      => $var['job-tags'],
            'job_weight'    => $var['job-weight'],
            'job_url'       => $var['job-url'],
            'url_status'    => $var['url-status'],
            // 'city_id'       => $var['city'],
            // 'district_id'   => $var['district'],
            // 'country_id'    => $var['country'],
            'date_created'  => $var['date-created'],
            // 'date_updated'  => date("Y-m-d"),
            'date_expired'  => $var['date-expired'],
            // 'job_snippet'   => $var['job-snippet'],
            );
        $location_fields = array(
            'city'          => $var['city'],
            'state'         => $var['state'],
            'country'       => $var['country'],
            );

        $query = db_select('zd_test_locations', 'l')
            ->fields('l', array('id'))
            ->condition('city', $location_fields['city'])
            ->condition('state', $location_fields['state'])
            ->condition('country', $location_fields['country'])
            ->execute();
        $num = $query->rowCount();
        if($num) {
            $job_fields['loc_id'] = $query->fetchField();
        } else {
            $insert = db_insert('zd_test_locations')
                    ->fields(array(
                        'city'      => $var['city'],
                        'state'     => $var['state'],
                        'country'   => $var['country'], 
                        ))
                    ->execute();
            $job_fields['loc_id'] = db_query("SELECT LAST_INSERT_ID()")->fetchField();
        }

        $status = db_merge('zd_test_jobs')
            ->key(array('job_id' => $var['job-id']?$var['job-id']:null))
            ->fields($job_fields)
            ->execute();
        if( $status == MergeQuery::STATUS_INSERT ) {
            $last_id = db_query("SELECT LAST_INSERT_ID()")->fetchField();
        } else {
            $last_id = $var['job-id'];
        }

        drupal_goto();
	}
?>